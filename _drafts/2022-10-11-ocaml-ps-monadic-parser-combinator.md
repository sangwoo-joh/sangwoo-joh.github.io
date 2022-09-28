---
layout: post
published: true
title: OCaml과 함께 PS를 -7-
subtitle: 파서 컴비네이터
---

## 발단
 - 예전에 kipa00님의 [OCaml로 문제
   풀이하기](https://www.acmicpc.net/blog/view/66) 글을 읽게된 후로 저
   문제를 너무 풀고 싶었음.
 - 하지만 kipa00님이 하신 것처럼 ocamllex이랑 ocamlyacc으로 풀면 재미
   없으니까 다른 걸 해보고 싶었다.
 - 그러던 차에 정말 놀랍게도 유튜브 추천 비디오로 Tsoding Daily라는
   스트리머의 [(의존성 없이) OCaml로 빠른 파서 컴비네이터 라이브러리
   밑바닥부터 만들기](https://www.youtube.com/watch?v=Y5IIXUBXvLs)라는
   동영상이 떴길래 애 재우고 나서 틀어놓고 멍때리고 놀았음.
 - 영상에 나온 레퍼런스인 [Monadic Parser
   Combinators](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwi0s7nUqrb6AhUkyYsBHUOaD-AQFnoECA0QAQ&url=https%3A%2F%2Fwww.cs.nott.ac.uk%2F~pszgmh%2Fmonparsing.pdf&usg=AOvVaw3LtR393c7YLbVqqhMb24Ty)
   페이퍼(라기엔 거의 매뉴얼에 가까운)와
   [Parcoom](https://github.com/tsoding/parcoom) 라이브러리 코드,
   그리고 [Dream](https://github.com/aantron/dream/) 덕분에 알고
   있었던 [Angstrom](https://github.com/inhabitedtype/angstrom/)
   라이브러리 코드까지 짬짬이 보다보니 도저히 구현하지 않고는 참지
   못하는 단계에 다다름.

## 내가 이해한 것들
 - 파서란 무엇인가
 - 파서 컴비네이터란 무엇인가
 - 컴비네이터 패턴
 - 모나드.. 가 뭔지는 위키에 잘 나와있으니 그걸 보시고


 준비가 다 되었으니 구현해보자.

## [2769: 논리식 비교](https://www.acmicpc.net/problem/2769)

 - 문제 설명
 - 탑다운으로, 먼저 표현식 타입과 그에 맞는 파서가 있다고 *가정* 하고,
   입력 받아서 구멍 뚫어놓고 파싱한 다음 문제 풀기. 변수 개수가 최대
   10개라서 $$ 2^{10} = 1024 $$ 개의 가능성을 다 살펴보면 된다
   (kipa00님의 문제 풀이 아이디어 참조)
 - 파서 타입
 - 입력 소모(consume)하기
 - 모나드를 위한 primitives
 - 컴비네이터들
 - 컴비네이터로 만든 기초 파서
 - Fix Point (Angstrom 구현 아이디어 참조)
 - Chaining
 - 준비가 다 되었다! 표현식 파서 하나씩 만들기
 - 표현식 파서 조립하기
 - 연산자 우선 순위를 어떻게 표현할 것인가? -> BNF 문법 자체에 드러날
   수 있다.
 - 완성된 파서
 - 입력 다듬기
 - 최종 결과


---

## References
 - [Parser Combinator](https://en.wikipedia.org/wiki/Parser_combinator)
 - [Angstrom](https://github.com/inhabitedtype/angstrom/)
 - [Parcoom](https://github.com/tsoding/parcoom) from [Tsoding
   Daily](https://www.youtube.com/watch?v=Y5IIXUBXvLs)
 - kipa00님의 [OCaml로 문제 풀이하기](https://www.acmicpc.net/blog/view/66)
 - [Combinator pattern](https://wiki.haskell.org/Combinator_pattern)
 - [Monadic Parser Combinators](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwi0s7nUqrb6AhUkyYsBHUOaD-AQFnoECA0QAQ&url=https%3A%2F%2Fwww.cs.nott.ac.uk%2F~pszgmh%2Fmonparsing.pdf&usg=AOvVaw3LtR393c7YLbVqqhMb24Ty)
 - [Monad](https://en.wikipedia.org/wiki/Monad_(functional_programming))
