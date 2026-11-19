// pdftool: small macOS helper for make_pdf.py
//   pdftool ocr <image> [<image> ...]      -> JSON array of {path, lines:[{text, conf, box:[x,y,w,h]}]}
//                                             box is normalized, origin bottom-left (same as PDF space)
//   pdftool doc <image> [<image> ...]      -> JSON [{path, quad:[[x,y]x4 tl,tr,br,bl] normalized, top-left origin, conf}]
//                                             (Apple's document segmentation, same as the Notes scanner)
//   pdftool render <pdf> <outdir> <dpi>   -> writes page-0001.png ... ; prints JSON [{page, png, w, h}]
// Uses Apple's Vision framework (on-device OCR) and PDFKit, so nothing leaves the Mac.
import Foundation
import Vision
import PDFKit
import AppKit
import ImageIO

func loadCG(_ path: String) -> CGImage? {
    let url = URL(fileURLWithPath: path) as CFURL
    guard let src = CGImageSourceCreateWithURL(url, nil) else { return nil }
    return CGImageSourceCreateImageAtIndex(src, 0, nil)
}

func ocr(_ path: String) -> [String: Any] {
    var out: [String: Any] = ["path": path, "lines": []]
    guard let img = loadCG(path) else { out["error"] = "cannot load"; return out }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = true
    if #available(macOS 13.0, *) { req.automaticallyDetectsLanguage = true }
    let handler = VNImageRequestHandler(cgImage: img, options: [:])
    do { try handler.perform([req]) } catch { out["error"] = "\(error)"; return out }
    var lines: [[String: Any]] = []
    for obs in (req.results ?? []) {
        guard let top = obs.topCandidates(1).first else { continue }
        let b = obs.boundingBox
        lines.append(["text": top.string, "conf": top.confidence,
                      "box": [b.origin.x, b.origin.y, b.size.width, b.size.height]])
    }
    out["lines"] = lines
    out["w"] = img.width; out["h"] = img.height
    return out
}

func pt(_ p: CGPoint) -> [Double] { return [Double(p.x), 1.0 - Double(p.y)] }

func doc(_ path: String) -> [String: Any] {
    var out: [String: Any] = ["path": path]
    guard let img = loadCG(path) else { out["error"] = "cannot load"; return out }
    let handler = VNImageRequestHandler(cgImage: img, options: [:])
    let seg = VNDetectDocumentSegmentationRequest()
    let rect = VNDetectRectanglesRequest()
    rect.maximumObservations = 4
    rect.minimumAspectRatio = 0.3
    rect.minimumSize = 0.3
    rect.quadratureTolerance = 30
    rect.minimumConfidence = 0.4
    try? handler.perform([seg, rect])
    if let r = seg.results?.first {
        out["quad"] = [pt(r.topLeft), pt(r.topRight), pt(r.bottomRight), pt(r.bottomLeft)]
        out["conf"] = r.confidence
    }
    out["rects"] = (rect.results ?? []).map { r in
        ["quad": [pt(r.topLeft), pt(r.topRight), pt(r.bottomRight), pt(r.bottomLeft)], "conf": r.confidence] as [String: Any]
    }
    return out
}

func render(_ pdf: String, _ outdir: String, _ dpi: Double) -> [[String: Any]] {
    guard let doc = PDFDocument(url: URL(fileURLWithPath: pdf)) else { return [] }
    try? FileManager.default.createDirectory(atPath: outdir, withIntermediateDirectories: true)
    var res: [[String: Any]] = []
    for i in 0..<doc.pageCount {
        guard let page = doc.page(at: i) else { continue }
        let bounds = page.bounds(for: .mediaBox)
        let rot = page.rotation % 180 != 0
        let wPt = rot ? bounds.height : bounds.width
        let hPt = rot ? bounds.width : bounds.height
        let size = NSSize(width: wPt * dpi / 72.0, height: hPt * dpi / 72.0)
        let thumb = page.thumbnail(of: size, for: .mediaBox)
        guard let tiff = thumb.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff),
              let png = rep.representation(using: .png, properties: [:]) else { continue }
        let path = String(format: "%@/page-%04d.png", outdir, i + 1)
        try? png.write(to: URL(fileURLWithPath: path))
        res.append(["page": i + 1, "png": path, "w": rep.pixelsWide, "h": rep.pixelsHigh])
    }
    return res
}

let args = CommandLine.arguments
guard args.count >= 3 else {
    FileHandle.standardError.write("usage: pdftool ocr <img...> | render <pdf> <outdir> <dpi>\n".data(using: .utf8)!)
    exit(2)
}
var result: Any = []
switch args[1] {
case "ocr": result = args.dropFirst(2).map { ocr($0) }
case "doc": result = args.dropFirst(2).map { doc($0) }
case "render": result = render(args[2], args.count > 3 ? args[3] : "/tmp", args.count > 4 ? Double(args[4]) ?? 150 : 150)
default: exit(2)
}
let data = try! JSONSerialization.data(withJSONObject: result, options: [])
FileHandle.standardOutput.write(data)
