---
layout: post
title: OCaml과 함께 PS를 -4-
subtitle: OCamlgraph 흉내내기
categories: ocdaml
background: '/assets/img/camels.jpeg'
---

 "최애 언어 [OCaml](https://ocaml.org/) 로 문제를 풀어보자!" 그 네
 번째 시리즈다.


#### 근황
 아빠가 되었다.

### [1068번 : 트리](https://www.acmicpc.net/problem/1068)
 트리의 리프 노드의 개수를 세는 문제
 문제 자체는 어렵지 않지만, 입력이 트리의 엣지 정보가 아니라 부모 정보가 들어옴. 그래서 첫 시도에 이상한거 했다가 헤맸음.
 "부모 정보로부터 트리를 만들기" 에 너무 매몰된듯. 다시 초심으로 돌아가서 OCamlgraph 흉내내기로 시도.
