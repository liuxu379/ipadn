# TestFlight diagnostic build (experimental)

This branch adds a local Swift package for the existing TestFlightKit sources and pins
AppleAuth v0.1.3 using the upstream published SDK SHA-256. The build script fetches and
verifies the SDK and generates the Xcode project with the local package linked.
Upstream: https://github.com/apple-auth/apple-auth/releases/tag/v0.1.3

The public SDK has no Device.importAccount API. Its documented loginStoreWithPET API
takes the AccountSession obtained from successful normal authentication directly.
The experimental adaptation uses that documented interface rather than a fake no-op
import method. Whether the public SDK has equivalent account binding and session
behavior is unverified; a real login must still pass Apple verification.
No new credential logging, device identities or verification bypass are added.

Build on macOS using the existing script iPadn-iOS/scripts/build_unsigned_ipa.sh.
The GitHub Actions workflow already invokes this script. The app must be compiled
with the local TestFlightKit package; success of an ordinary build is not evidence
of successful authentication. No real Apple account credentials belong in CI.

Full Xcode compilation, package linking, simulator tests and authorized device login
are still required. Do not treat this branch as a confirmed login fix.

## Login-only build after native linker failure

Run 45987017907 confirmed that the pinned Swift SDK compiles but does not
export the private tf_* archive shim required by TFSINF. The diagnostic
package therefore defines TF_LOGIN_DIAGNOSTIC_ONLY. The existing native
implementation is preserved behind a conditional compilation flag. The
diagnostic variant explicitly throws for archive writes and verification,
returns unavailable indicators for inspection, and blocks TestFlight
downloads and installation at their entry points. It is not a replacement
for the original archive library. No authorization data or archive checks
are fabricated. The scope is testing ordinary account authentication and
collecting the redacted diagnostic logs. Full functionality requires the
original compatible archive dependency and further validation.

## Faster diagnostic iteration

The device IPA in run 45988919931 built and passed packaging checks; subsequent
simulator test compilation failed because CoreTests did not import TestFlightKit.
The conditional import and explicit test target package dependency are added.
Automatic PR builds on diagnostic-v2.3.5 now run offline formatter and existing
static checks, compile and verify device IPAs, and upload artifacts. They skip the
full simulator suite and separate iOS 16 compatibility job. Full testing remains
available via manual workflow dispatch with run_tests enabled (and the separate
iOS 16 workflow); no production release requirements are relaxed. Go and Rust
dependency caches are keyed to the pinned inputs; SDK verification remains mandatory.
Fast diagnostic builds are not release validation or proof of login success.
