// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "TestFlightKit",
    platforms: [.iOS(.v16)],
    products: [.library(name: "TestFlightKit", targets: ["TestFlightKit"])],
    dependencies: [.package(path: "../vendor/AppleAuth")],
    targets: [
        .target(name: "TestFlightKit",
                dependencies: [.product(name: "AppleAuth", package: "AppleAuth")],
                path: ".", exclude: ["Package.swift"],
                swiftSettings: [.define("TF_LOGIN_DIAGNOSTIC_ONLY")])
    ]
)
