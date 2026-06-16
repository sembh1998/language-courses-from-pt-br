#import "@preview/cmarker:0.1.3": render
#import "theme.typ": *

#let topic = sys.inputs.at("topic", default: "topics/a1/001-alfabeto-alemao-e-sons-basicos")
#let course-label = sys.inputs.at("course-label", default: "Alemão para PT-BR")
#let target-language-pt = sys.inputs.at("target-language-pt", default: "alemão")
#let lesson-number = sys.inputs.at("lesson-number", default: none)
#let lesson = read(topic + "/lesson.md")

#show: doc => workbook(doc, title: "Lição de " + target-language-pt, kind: "Lição", accent: teal, course-label: course-label, lesson-number: lesson-number, margin: (x: 1.3cm, y: 1.3cm), body-size: 9.9pt)

#render(lesson)
