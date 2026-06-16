#import "@preview/cmarker:0.1.3": render
#import "theme.typ": *

#let topic = sys.inputs.at("topic", default: "topics/a1/001-alfabeto-alemao-e-sons-basicos")
#let course-label = sys.inputs.at("course-label", default: "Alemão para PT-BR")
#let target-language-pt = sys.inputs.at("target-language-pt", default: "alemão")
#let lesson-number = sys.inputs.at("lesson-number", default: none)
#let story = read(topic + "/story.md")

#show: doc => workbook(doc, title: "História em " + target-language-pt, kind: "História", accent: amber, course-label: course-label, lesson-number: lesson-number, margin: (x: 1.3cm, y: 1.3cm), body-size: 9.9pt)

#render(story)
