---
layout: post
published: true
title: Emacs 28 짧은 소감
subtitle: --with-nativecomp
category: dev
---

 이맥스는 참 재밌고 나에겐 최고의 에디터지만, 가끔 성능이 부족하다고
 느껴질 때가 있다. 지금 사용하는 데스크탑이 최신은 아니지만 그래도
 i7-7700 8코어에 램 16기가인데도 꽤 자주 버벅거리곤 한다. 아마도
 Elisp의 태생적 한계라고 짐작한다.

 그래도 어떻게 꾸역꾸역 잘 사용해왔다가, 연말맞이 & 새해기념으로
 에디터 설정을 싹 업그레이드하면서 이 블로그의 이름대로 ~~야크~~낙타
 털깎기를 진행해보았다. 다음은 의식의 흐름이다.

  - 왜 이맥스는 런칭 속도도 느리고 가끔씩 입력하다가 미묘한 stall이
    발생할까?
  - 아마도 내 `.emacs` 세팅의
    문제겠지. [최적화해보자](https://github.com/sangwoo-joh/dotfiles/tree/master/emacs).
  - 안쓰는 패키지 지우고, 의미없는 함수 호출 다 지우고, 바이트코드
    컴파일하게 했더니 런칭 속도는 빨라졌는데 여전히 stall은 있네.
  - elisp 바이트코드 인터프리터가 느린거 같은데, 네이티브 플러그인은
    못만드나?
  - 찾아보니 이맥스 25부터 [Dynamic
    Modules](https://www.gnu.org/software/emacs/manual/html_node/elisp/Dynamic-Modules.html)
    라는 일종의 C-FFI를 지원하고, 덕분에
    [Ecaml](https://github.com/janestreet/ecaml)을 쓰면 OCaml로 모듈을
    짤 수 있구나!! 감사합니다 JaneStreet.
  - 그런데 지금 내가 쓰는 이맥스 27에서는 [Ecaml을
    못쓰네](https://github.com/janestreet/ecaml/issues/6). 다음 버전
    릴리즈 때나 고쳐지겠군...
  - 플러그인 말고 elisp 자체를 네이티브 코드로 컴파일하는 도구는 없나?
  - 찾아보니 1년 동안 개발되고 있는
    [GccEmacs](https://www.emacswiki.org/emacs/GccEmacs)라는게
    있구나. 심지어 [톡](https://youtu.be/zKHYZOAc_bQ)도 했었군.

...까지 돌다 와서, 당장 새 버전을 빌드해서 사용해보고 있다.

### 이맥스 28 + 네이티브 컴파일러
 1. 일단 이맥스 코드를 클론
    받는다. `git://git.savannah.gnu.org/emacs.git` 을 클론해도 되고
    미러인 `https://github.com/emacs-mirror/emacs`를 클론해도 된다.
 2. `feature/native-comp` 브랜치에 체크아웃 한다.
 3. GCC-10, 그리고 네이티브 컴파일러를 위한 libgccjit 디펜던시를
    설치한 뒤에 빌드한다:

``` sh
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt-get install gcc-10 g++-10 libgccjit0 libgccjit10-dev libjansson4 libjansson-dev
export CC=/usr/bin/gcc-10 CXX=/usr/bin/gcc-10
./autogen.sh
./configure --with-nativecomp
make -jN
sudo make install
emacs --version  # shows GNU Emacs 28.0.50
```

 이렇게하면 Elisp 네이티브 컴파일러가 탑재된 이맥스가
 설치된다. 기본적으로 모든 Elisp 코드(`*.el`)는 바이트코드(`*.elc`)로
 컴파일 할 수 있는데, 네이티브 컴파일러 덕분에 이제는 네이티브
 코드(`*.eln`)로도 컴파일 가능하다.

 디폴트로 모든 `*.el` 파일을 Deferred 컴파일, 즉 "just-in-time"
 네이티브 컴파일하게 되어 있다. 바이트코드로 컴파일된 Elisp 모듈이
 로드되면, 네이티브 컴파일 큐에다 그 모듈을 넣어두고, 큐에서 하나씩
 빼서 뒤에서 async하게 네이티브 빌드를 진행하는 방식이다. 네이티브
 컴파일이 끝나면 자동으로 바이트코드를 대체한다.

 내 이맥스 세팅에도 [`with-nativecomp` 브랜치를
 추가하여](https://github.com/sangwoo-joh/dotfiles/tree/with-native-comp)
 새로운 네이티브 컴파일 기능을 다 적용해보았다. `(native-compile-async
 DIR 'recursively)` 한줄이면 `DIR` 안의 모든 모듈을 다 빌드할 수 있다.

### Elisp과 네이티브 컴파일러
 [Andrea
 Corallo](https://www.linkedin.com/in/andrea-corallo/?originalSubdomain=fr)
 라는 ARM의 컴파일러 엔지니어의 주도로 Elisp 코드를 네이티브 코드로
 컴파일 하는 기능을 약 1년간 구현하고 있는 것 같다. 톡을 보니 몰랐던
 이맥스 코드의 대략적인 상황을 알 수 있었는데,
  * 이맥스는 주로 Elisp 구현체다. 거의 80% 가까이가 Elisp으로
    짜여있다.
  * 나머지 20%는 C로 짜여있는데 주로 성능 문제 때문이다. 대부분의
    primitives 함수와 Elisp 인터프리터가 이걸로 구현되어 있는 것 같다.
  * Elisp은 느리다 (...).
  * Elisp 인터프리터는 C로 짜여있지만, Elisp 바이트코드 최적화는
    Elisp으로 짜여져 있다. 즉 부트스트래핑 해야 한다.

 하여튼 간에 핵심은 Elisp이 느리다는 것이다. 정확히는 지금의 Elisp
 인터프리터와 바이트코드 컴파일러가 느리다. 재밌는 것은 바이트코드
 컴파일 최적화 코드인 `byte-opt.el` 파일의 주석에 다음과 같이 쓰여져
 있다는 점이다:

> "No matter how hard you try, you can't make a racehorse out of a
> pig. You can, however, make a faster pig."

 빠른 돼지를 만들긴 했지만 여전히 돼지인 것이다. 아무튼 그래서 크게 두
 축에서 이 느린 돼지를 더 빠르게 시도가 있어 왔는데, 하나는 아예
 Elisp이 아닌 새로운 언어를 만들어서 거기 위에서 새롭게 이맥스를 다시
 만드는 것이고[^1], 다른 하나가 바로 Elisp 코드를 네이티브 코드로
 컴파일하려는 이 시도이다[^2]. 일단 Elisp 코드를 전부 재활용할 수 있기
 때문에 이게 훨씬 더 좋은 시도로 보인다. 그리고 이미 Elisp을 참 재밌게
 쓰고 있어서, 굳이 Guile 로 옮겨야 하나 싶다(...).

 참 대단한 사람이다. 덕분에 Elisp은 네이티브 코드로 컴파일 할 수 있게
 되었다. 그리고 n년간 이맥스를 잘 쓰고 있으면서 한번도 이맥스 소스
 코드를 볼 생각은 하지 못했었는데, 이번 기회에 슬쩍 읽어 봐야겠다.


### 짧은 감상
 첫 구동 시에는 네이티브 JIT 컴파일을 해야해서 CPU 가동률이 높았는데,
 이게 끝난 이후로는 확실히 반응속도가 빠릿빠릿(?)한 기분이다. 일단
 구동 속도가 빨라진 것은 확실히 체감된다. 그리고 지금 사용 중인
 테마에서 키 입력이나 반응속도가 빨라진 것도 체감 된다. 아예 stall이
 없진 않지만, 예전에 비해서 눈에 띄게 줄었다. 자동완성 기능이 동작하는
 속도도 확연히 빨라졌다. 아직 길게 사용해본 것은 아니지만, 지금까지는
 큰 버그나 이슈를 겪진 않았다.

 이맥스 28이 언제 릴리즈할진 모르겠고, 또 네이티브 컴파일러가 28
 릴리즈에 포함될지도 모르겠지만, 당분간은 이렇게 직접 빌드한 이맥스를
 쭉 사용해보려고 한다. 그리고 당연하게도 이 글은 직접 빌드한 이맥스 28
 네이티브 컴파일러 탑재 버전에서 작성하고 있다.

 오늘의 털깎기 끝.

---
[^1]: [Guile-emacs](https://www.emacswiki.org/emacs/GuileEmacs)라고 하며, 이 [Guile](https://www.gnu.org/software/guile/) 이라는 언어는 Rust로 개발한다고 한다. 근데 이러면 돼지가 아니라 아예 다른 생물이 되는 게 아닌지?

[^2]: 저자는 돼지에 날개를 달아주는 거라고 설명한다 (...)
