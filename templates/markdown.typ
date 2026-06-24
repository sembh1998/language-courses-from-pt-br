#import "@preview/cmarker:0.1.3": render
#import "theme.typ": *

#let file = sys.inputs.at("file")
#let title = sys.inputs.at("title", default: "Material")
#let kind = sys.inputs.at("kind", default: "Material")
#let course-label = sys.inputs.at("course-label", default: "Alemão para PT-BR")
#let lesson-number = sys.inputs.at("lesson-number", default: none)
#let content = read(file)

#show: doc => workbook(doc, title: title, kind: kind, accent: rose, course-label: course-label, lesson-number: lesson-number, margin: (x: 1.3cm, y: 1.3cm), body-size: 9.6pt)

#render(content)
