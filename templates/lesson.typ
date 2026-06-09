#import "@preview/cmarker:0.1.3": render
#import "theme.typ": *

#let topic = sys.inputs.at("topic", default: "topics/a1/001-alfabeto-alemao-e-sons-basicos")
#let lesson = read(topic + "/lesson.md")

#show: doc => workbook(doc, title: "Lição de alemão", kind: "Lição", accent: teal, margin: (x: 1.3cm, y: 1.3cm), body-size: 9.9pt)

#render(lesson)
