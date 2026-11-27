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
