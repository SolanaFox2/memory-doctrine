"""
tests/test_confidence.py
------------------------
TDD tests for kpm_builder.confidence.confidence().

Written BEFORE the implementation — run first to confirm all RED, then GREEN
after confidence.py is created.
"""
import pytest

from kpm_builder.schema import SourceTier, ConfidenceBucket
from kpm_builder.confidence import (
    confidence,
    TIER_CAP,
    BUCKET_RANK,
    _downgrade,
    _min_bucket,
)

S = ConfidenceBucket.SUPPORTED
P = ConfidenceBucket.PARTIAL
U = ConfidenceBucket.UNVERIFIED


# ---------------------------------------------------------------------------
# Module-constant contracts
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_tier_cap_keys_cover_all_tiers(self):
        """TIER_CAP must have an entry for every SourceTier member."""
        assert set(TIER_CAP.keys()) == set(SourceTier)

    def test_bucket_rank_ordering(self):
        """SUPPORTED must rank highest; UNVERIFIED lowest."""
        assert BUCKET_RANK[S] > BUCKET_RANK[P] > BUCKET_RANK[U]

    def test_tier_cap_values(self):
        assert TIER_CAP[SourceTier.PEER_REVIEWED]   == S
        assert TIER_CAP[SourceTier.PREPRINT]         == S
        assert TIER_CAP[SourceTier.OFFICIAL_DOCS]    == S
        assert TIER_CAP[SourceTier.REPUTABLE_PRESS]  == P
        assert TIER_CAP[SourceTier.BLOG]             == P
        assert TIER_CAP[SourceTier.UNKNOWN]          == U


# ---------------------------------------------------------------------------
# Helper: _downgrade
# ---------------------------------------------------------------------------

class TestDowngrade:
    def test_supported_becomes_partial(self):
        assert _downgrade(S) == P

    def test_partial_becomes_unverified(self):
        assert _downgrade(P) == U

    def test_unverified_stays_unverified(self):
        assert _downgrade(U) == U


# ---------------------------------------------------------------------------
# Helper: _min_bucket
# ---------------------------------------------------------------------------

class TestMinBucket:
    def test_min_of_equal(self):
        assert _min_bucket(S, S) == S

    def test_min_supported_partial(self):
        assert _min_bucket(S, P) == P

    def test_min_partial_unverified(self):
        assert _min_bucket(P, U) == U

    def test_min_supported_unverified(self):
        assert _min_bucket(S, U) == U


# ---------------------------------------------------------------------------
# Ground gate (overrides all)
# ---------------------------------------------------------------------------

class TestGroundGate:
    def test_reject_peer_reviewed_is_unverified(self):
        """Rule 1: reject → UNVERIFIED, regardless of tier or corroborations."""
        result = confidence(
            tier=SourceTier.PEER_REVIEWED,
            n_independent_corroborations=10,
            ground_verdict="reject",
            has_unresolved_contradiction=False,
        )
        assert result == U

    def test_reject_unknown_is_unverified(self):
        result = confidence(
            tier=SourceTier.UNKNOWN,
            n_independent_corroborations=0,
            ground_verdict="reject",
            has_unresolved_contradiction=True,
        )
        assert result == U

    def test_reject_blog_with_contradiction_is_unverified(self):
        result = confidence(
            tier=SourceTier.BLOG,
            n_independent_corroborations=5,
            ground_verdict="reject",
            has_unresolved_contradiction=True,
        )
        assert result == U


# ---------------------------------------------------------------------------
# Tier cap
# ---------------------------------------------------------------------------

class TestTierCap:
    def test_blog_entails_many_corroborations_is_partial(self):
        """Tier cap BLOG→PARTIAL; corroboration cannot exceed cap."""
        result = confidence(
            tier=SourceTier.BLOG,
            n_independent_corroborations=5,
            ground_verdict="entails",
            has_unresolved_contradiction=False,
        )
        assert result == P

    def test_unknown_entails_is_unverified(self):
        """Tier cap UNKNOWN→UNVERIFIED."""
        result = confidence(
            tier=SourceTier.UNKNOWN,
            n_independent_corroborations=10,
            ground_verdict="entails",
            has_unresolved_contradiction=False,
        )
        assert result == U

    def test_reputable_press_entails_many_is_partial(self):
        """Tier cap REPUTABLE_PRESS→PARTIAL; corroboration can't raise it."""
        result = confidence(
            tier=SourceTier.REPUTABLE_PRESS,
            n_independent_corroborations=99,
            ground_verdict="entails",
            has_unresolved_contradiction=False,
        )
        assert result == P

    def test_official_docs_entails_two_is_supported(self):
        """OFFICIAL_DOCS cap is SUPPORTED; with ≥2 corroborations → SUPPORTED."""
        result = confidence(
            tier=SourceTier.OFFICIAL_DOCS,
            n_independent_corroborations=2,
            ground_verdict="entails",
            has_unresolved_contradiction=False,
        )
        assert result == S


# ---------------------------------------------------------------------------
# over_claims cap
# ---------------------------------------------------------------------------

class TestOverClaimsCap:
    def test_peer_reviewed_over_claims_many_is_partial(self):
        """Rule 3: over_claims caps at PARTIAL even with top tier + 5 corroborations."""
        result = confidence(
            tier=SourceTier.PEER_REVIEWED,
            n_independent_corroborations=5,
            ground_verdict="over_claims",
            has_unresolved_contradiction=False,
        )
        assert result == P

    def test_over_claims_on_blog_stays_partial(self):
        """over_claims on a BLOG-tier (cap=PARTIAL) stays PARTIAL (min(P,P)=P)."""
        result = confidence(
            tier=SourceTier.BLOG,
            n_independent_corroborations=5,
            ground_verdict="over_claims",
            has_unresolved_contradiction=False,
        )
        assert result == P

    def test_over_claims_on_unknown_stays_unverified(self):
        """over_claims on UNKNOWN (cap=UNVERIFIED) stays UNVERIFIED."""
        result = confidence(
            tier=SourceTier.UNKNOWN,
            n_independent_corroborations=5,
            ground_verdict="over_claims",
            has_unresolved_contradiction=False,
        )
        assert result == U


# ---------------------------------------------------------------------------
# Corroboration rule
# ---------------------------------------------------------------------------

class TestCorroborationRule:
    def test_peer_reviewed_entails_two_corroborations_is_supported(self):
        """Rule 4: SUPPORTED held with ≥2 corroborations."""
        result = confidence(
            tier=SourceTier.PEER_REVIEWED,
            n_independent_corroborations=2,
            ground_verdict="entails",
            has_unresolved_contradiction=False,
        )
        assert result == S

    def test_peer_reviewed_entails_one_corroboration_is_partial(self):
        """Rule 4: SUPPORTED dropped to PARTIAL with only 1 corroboration."""
        result = confidence(
            tier=SourceTier.PEER_REVIEWED,
            n_independent_corroborations=1,
            ground_verdict="entails",
            has_unresolved_contradiction=False,
        )
        assert result == P

    def test_peer_reviewed_entails_zero_corroborations_is_partial(self):
        """Rule 4 edge: 0 corroborations also drops SUPPORTED → PARTIAL."""
        result = confidence(
            tier=SourceTier.PEER_REVIEWED,
            n_independent_corroborations=0,
            ground_verdict="entails",
            has_unresolved_contradiction=False,
        )
        assert result == P

    def test_blog_one_corroboration_stays_partial(self):
        """Rule 4 only acts on SUPPORTED; BLOG cap=PARTIAL is unchanged by corroboration count."""
        result = confidence(
            tier=SourceTier.BLOG,
            n_independent_corroborations=1,
            ground_verdict="entails",
            has_unresolved_contradiction=False,
        )
        assert result == P

    def test_preprint_two_corroborations_is_supported(self):
        """Preprint cap=SUPPORTED; with ≥2 corroborations → SUPPORTED."""
        result = confidence(
            tier=SourceTier.PREPRINT,
            n_independent_corroborations=2,
            ground_verdict="entails",
            has_unresolved_contradiction=False,
        )
        assert result == S

    def test_preprint_one_corroboration_is_partial(self):
        """Preprint cap=SUPPORTED; only 1 corroboration → PARTIAL."""
        result = confidence(
            tier=SourceTier.PREPRINT,
            n_independent_corroborations=1,
            ground_verdict="entails",
            has_unresolved_contradiction=False,
        )
        assert result == P


# ---------------------------------------------------------------------------
# Unresolved contradiction downgrade
# ---------------------------------------------------------------------------

class TestUnresolvedContradiction:
    def test_supported_with_contradiction_becomes_partial(self):
        """Rule 5: SUPPORTED → PARTIAL when has_unresolved_contradiction."""
        result = confidence(
            tier=SourceTier.PEER_REVIEWED,
            n_independent_corroborations=2,
            ground_verdict="entails",
            has_unresolved_contradiction=True,
        )
        assert result == P

    def test_partial_with_contradiction_becomes_unverified(self):
        """Rule 5: PARTIAL → UNVERIFIED."""
        result = confidence(
            tier=SourceTier.REPUTABLE_PRESS,
            n_independent_corroborations=5,
            ground_verdict="entails",
            has_unresolved_contradiction=True,
        )
        assert result == U

    def test_unverified_with_contradiction_stays_unverified(self):
        """Rule 5: UNVERIFIED → UNVERIFIED (floor)."""
        result = confidence(
            tier=SourceTier.UNKNOWN,
            n_independent_corroborations=0,
            ground_verdict="entails",
            has_unresolved_contradiction=True,
        )
        assert result == U

    def test_no_contradiction_flag_does_not_downgrade(self):
        """Sanity: False flag leaves result unchanged."""
        result = confidence(
            tier=SourceTier.PEER_REVIEWED,
            n_independent_corroborations=2,
            ground_verdict="entails",
            has_unresolved_contradiction=False,
        )
        assert result == S


# ---------------------------------------------------------------------------
# Multi-rule interactions (combined)
# ---------------------------------------------------------------------------

class TestInteractions:
    def test_over_claims_plus_contradiction_peer_reviewed(self):
        """over_claims caps at PARTIAL; contradiction downgrades PARTIAL→UNVERIFIED."""
        result = confidence(
            tier=SourceTier.PEER_REVIEWED,
            n_independent_corroborations=5,
            ground_verdict="over_claims",
            has_unresolved_contradiction=True,
        )
        assert result == U

    def test_one_corroboration_plus_contradiction_peer_reviewed(self):
        """1 corroboration → PARTIAL; contradiction → UNVERIFIED."""
        result = confidence(
            tier=SourceTier.PEER_REVIEWED,
            n_independent_corroborations=1,
            ground_verdict="entails",
            has_unresolved_contradiction=True,
        )
        assert result == U

    def test_reject_overrides_everything(self):
        """reject gate fires before over_claims or contradiction logic."""
        result = confidence(
            tier=SourceTier.PEER_REVIEWED,
            n_independent_corroborations=99,
            ground_verdict="reject",
            has_unresolved_contradiction=False,
        )
        assert result == U
