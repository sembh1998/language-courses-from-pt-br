#let input = sys.inputs.at("input")
#let page-count = int(sys.inputs.at("pages"))
#let padded-count = calc.ceil(page-count / 4) * 4
#let sheet-count = int(padded-count / 4)

#set page(width: 297mm, height: 210mm, margin: 0pt)

#let source-page(n) = if n <= page-count {
  image(input, page: n, width: 100%, height: 100%, fit: "contain")
} else {
  block(width: 100%, height: 100%)[ ]
}

#let spread(left, right) = grid(
  columns: (1fr, 1fr),
  gutter: 0pt,
  source-page(left),
  source-page(right),
)

#for sheet in range(0, sheet-count) {
  let front-left = padded-count - (2 * sheet)
  let front-right = 1 + (2 * sheet)
  let back-left = 2 + (2 * sheet)
  let back-right = padded-count - 1 - (2 * sheet)

  spread(front-left, front-right)
  pagebreak()
  spread(back-left, back-right)
  if sheet < sheet-count - 1 {
    pagebreak()
  }
}
