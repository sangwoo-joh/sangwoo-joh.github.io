---
layout: post
published: true
title: Spacetime
categories: ocaml
---

OCaml 4.04 버전부터 Spacetime이라는 프로파일러가 들어갔다. 제인
스트리트에서 이와 관련된
[포스팅](https://blogs.janestreet.com/a-brief-trip-through-spacetime/)을
해서 번역으로 남겨본다.

## Spacetime 훑어보기

Spacetime은 메모리 누수와 원치 않는 메모리 할당을 찾아내기 위한 새로운
프로파일링 도구이다. 아직 거칠지만, 아주 유용한 도구이다. Spacetime
문서가 별로 없기 때문에 어떻게 쓰는지 간단히 기록해본다.

### 프로파일 생성하기

예시로 `js_of_ocaml`을 프로파일링해보자. 일단 spacetime을 쓸 수 있는
Ocaml 컴파일러가 필요하다.

```bash
$ opam switch 4.04.0+spacetime
$ eval `opam config env`
```

이 컴파일러로 실행 파일을 빌드해야 한다. 이경우 그냥 `opam`으로
설치하면 된다.

이제 환경 변수 `OCAML_SPACETIME_INTERVAL`로 프로파일링을 켜고
Spacetime이 OCaml 힙을 얼마나 자주 감시할 건지 명시해준 다음 실행하면
된다. 단위는 밀리세컨드 단위이다.

```bash
$ OCAML_SPACETIME_INTERVAL=1000 js_of_ocaml core_kernel.cma
```

이렇게 실행하면 그냥 실행하는 것보다 느리고 메모리도 더 잡아먹긴
하지만 힙 메모리 자체에는 영향을 주지 않는다. 실행이 끝나면
`spacetime-` 접두어가 붙은 파일이 생성된다.

```bash
$ ls | grep spacetime
spacetime-8045
```

8045는 단순히 실행됐던 프로세스의 pid이다. 실행 파일이 fork 하는 경우
여러개의 spacetime 파일이 생길 것이다.

이제 우리는 spacetime 프로파일을 얻었다. 이제 프로파일을 보기 위한
`prof_spacetime`을 설치 후 실행하자.

```bash
$ opam switch 4.04.0
$ eval `opam config env`
$ opam install prof_spacetime
$ prof_spacetime process -e .opam/4.04.0+spacetime/bin/js_of_ocaml spacetime-8045
Processing series...done
$ ls | grep spacetime
spacetime-8045
spacetime-8045.p
```

약간 시간이 걸린다. `js_of_ocaml`의 경우 몇 분 정도 걸린다. `-e`
옵션은 `prof_spacetime`에 프로파일을 생성한 실행 파일을
전달해준다. 강요되는 옵션은 아니지만, 이게 없으면 C 코드의 위치를 알지
못한다.

### 웹 뷰어

이제 프로파일을 볼 준비가 됐다. 웹 뷰어로 볼 수 있다.

```bash
$ prof_spacetime serve -p spacetime-8045.p
Processing series...done
Serving on 127.0.0.1:8000
```

#### Live words

브라우저로 해당 주소에 들어가면 흥미롭게 화려한 색의 그래프가
반겨준다.

![Spacetime
graph](https://blog.janestreet.com/a-brief-trip-through-spacetime/spacetime1.png)

이 그래프는 live words, 즉 프로그램 실행 도중 살아있는 워드들을
보여주는데, 각각의 워드가 할당된 소스 위치를 담고 있다. 그래서
마우스를 그래프의 특정 부분에 갖다 대면 그 부분의 소스 위치를
보여준다.

![Spacetime
mouseover](https://blog.janestreet.com/a-brief-trip-through-spacetime/spacetime2.png)

그리고 그 부분을 클릭하면 새로운 그래프를 만들어준다.

![Spacetime
subgraph](https://blog.janestreet.com/a-brief-trip-through-spacetime/spacetime3.png)

이 그래프는 클릭한 소스 위치에서 할당된 live 워드들만 담고
있다. 그리고 실제로 할당을 실시한 함수 호출의 소스 위치, 즉 백
트레이스(backtrace)의 다음 프레임으로 나뉘어져 있다. 이게 바로
Spacetime의 핵심 기능이다: 이 워드들이 `List.map`으로 할당됐을 뿐만
아니라, 어떤 함수가 `List.map`을 호출해서 그것들을 할당했는지 볼 수
있다. 그래프들을 계속 클릭하다보면 결국 어떤 워드가 할당되는 전체 백
트레이스를 다 볼 수 있다.

![Spacetime
subgraph](https://blog.janestreet.com/a-brief-trip-through-spacetime/spacetime4.png)

백트레이스의 제일 윗 링크를 클릭하면 원래 그래프로 돌아간다.

#### 할당된 워드들

live 그래프(live 워드와 live 블록들)는 메모리 누수를 찾아낼 때
유용하다. 원치 않는 할당을 없애기 위해서는 할당 그래프가 더
유용하다. "All allocated word" 링크를 클릭하면 다음과 같은 그래프를
보여준다.

![Spacetime
subgraph](https://blog.janestreet.com/a-brief-trip-through-spacetime/spacetime5.png)

이 그래프는 프로그램 안에서 누적되는 총 할당을 보여준다. 역시 각각
할당의 소스 위치를 담고 있다. 마우스를 한 부분에 갖다대면 그 부분의
할당을 보여준다. 클릭하면 그 위치의 할당만 보여주고, 백 트레이스의
다음 프레임으로 나뉘어 진다.

### 터미널 뷰어

터미널에서도 볼 수 있다.

```bash
$ prof_spacetime view -p spacetime-8045.p
```

이러면 람다 스타일로 터미널 뷰어가 실행된다.

![Spacetime
subgraph](https://blog.janestreet.com/a-brief-trip-through-spacetime/spacetime6.png)

역시 프로그램의 특정 실행 시간(1.07844초)에서의 live 워드들을
보여준다. 역시 워드가 할당된 소스 위치로 나뉘어져 있다. 좌우 방향키로
다른 점을 볼 수 있고, 상하 방향키로 다른 행을 선택할 수 있다. 엔터
키는 선택한 행에 대해서 아래와 같은 뷰를 보여준다.

![Spacetime
subgraph](https://blog.janestreet.com/a-brief-trip-through-spacetime/spacetime7.png)

이러면 선택한 소스 위치(`memory.c: 552`)에서 할당된 워드들을
보여준다. 역시 메모리 할당을 포함하는 함수를 호출하는 소스 위치로
나뉘어져 있다. 즉, 백트레이스의 다음 프레임들이다. 백스페이스 키로
이전 뷰로 돌아갈 수 있다.

마지막으로, 탭 키로 세 가지 모드를 고를 수 있다: live 워드들, live
블록들, 그리고 할당된 워드들. `q` 키로 종료하면 된다.

## 뱀발

이거 완전 [perf](https://perf.wiki.kernel.org/index.php/Main_Page)
아니냐? 싶을 정도로 C 프로파일러인 perf와 거의 같다. 실제 OCaml 코드가
컴파일 될 때 `caml` 접두어 같은 레이블을 써서 어셈블리를 뽑기도 하고,
C 베이스로 구현되어 있기도 해서 실제로 perf로 프로파일링 할 수 있긴
하다.

다만 웹 뷰어로 그래프를 볼 수 있다는 건 정말 강점이다. 시각화는 정말
큰 도움이 되기 때문이다. 그리고 패키지 매니저에서 직접 이런 도구를
제공한다는 건 정말 좋은 신호다. 관리되고 있는 언어라는
의미니까. OCaml이여 영원하라.


출처: [A brief trip through
Spacetime](https://blogs.janestreet.com/a-brief-trip-through-spacetime/)
