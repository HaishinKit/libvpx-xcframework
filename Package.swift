// swift-tools-version: 5.9
import PackageDescription
let package = Package(
    name: "libvpx",
    platforms: [.iOS(.v13), .tvOS(.v13), .macOS(.v11), .macCatalyst(.v14), .visionOS(.v1)],
    products: [.library(name: "libvpx", targets: ["libvpx"])],
    targets: [.binaryTarget(name: "libvpx", url: "https://github.com/HaishinKit/libvpx-xcframework/releases/download/v1.17.1/libvpx.xcframework.zip", checksum: "245a4b7114707f0f0e221f1dfb76ba81ae5f2252f45bee6783f7256084a45e09")]
)
