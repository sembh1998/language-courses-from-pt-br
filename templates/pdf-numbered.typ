#let input = sys.inputs.at("input")
#let page-count = int(sys.inputs.at("pages"))
#let start-at = int(sys.inputs.at("start", default: "1"))

#set page(width: 210mm, height: 297mm, margin: 0pt)

#let page-number(n) = place(
  bottom + center,
  dy: -7mm,
  rect(
    fill: white.transparentize(15%),
    radius: 3pt,
    inset: (x: 5pt, y: 2pt),
  )[
    #text(size: 8pt, weight: "bold")[#str(n)]
  ],
)

#for source-page in range(1, page-count + 1) {
  image(input, page: source-page, width: 100%, height: 100%, fit: "stretch")
  page-number(start-at + source-page - 1)
  if source-page < page-count {
    pagebreak()
  }
}
