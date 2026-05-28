#import "@preview/cmarker:0.1.3": render
#import "theme.typ": *

#let topic = sys.inputs.at("topic", default: "topics/a1/001-alfabeto-alemao-e-sons-basicos")
#let lesson = read(topic + "/lesson.md")

#show: doc => workbook(doc, title: "German Lesson", kind: "Lesson", accent: teal, margin: (x: 1.8cm, y: 1.85cm), body-size: 10.6pt)

#render(lesson)
