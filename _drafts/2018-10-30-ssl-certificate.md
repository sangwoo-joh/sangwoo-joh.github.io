---
layout: post
title: "TLS Certificate and Opam"
categories: linux
author: "Sangwoo Joh"
---

## TLS Certificate

### 발단
회사 *nix 세팅을 하다보면 평소에는 만날 수 없던 다양한 이슈에 봉착하게
된다.  보안을 위해 많은 제약이 있다보니 어쩔 수 없는 일이긴 하지만
귀찮긴 하다.  OCaml 찬동자기 때문에 일단 opam부터 깔고 시작했는데,
초기 프록시 세팅에서는 잘 되던 친구가 갑자기 안되기 시작했다.
친절하게 `~/.opam/log` 디렉토리의 `*.err` 파일을 까보니 다음과 같은
메시지를 확인할 수 있었다.

> curl: (60) SSL certificate problem: unable to get local issuer
> certificate More details here:
>
> https://curl.haxx.se/docs/sslcerts.html
>
> curl failed to verify the legitimacy of the server and therefore
> could not establish a secure connection to it. To learn more about
> this situation and how to fix it, please visit the web page
> mentioned above.

프록시만 설정하면 되는 줄 알았더니 인증서 설정도 해줘야 하는
것이었다. (그럼 왜 초반 프록시만 설정했을 때는 동작했던걸까? 의문...)

### 해결
opam은 패키지 다운로드를 위해 내부적으로 curl을 사용하고, 그 curl의
ssl 인증서 관련 오류로 인한 문제인걸 바로 파악할 수 있었다.  너무도
친절하게 [링크](https://curl.haxx.se/docs/sslcerts.html)에서 문제
해결을 하라고 했으니 링크를 따라가보자.

`opam update --debug`로 다 출력해보니, 제일 첫번째 failure는
`https://opam.ocaml.org/1.2.2/urls.txt` 를 curl로 받아오는 부분이있다.
그냥 커맨드로 `curl --cacert .cert` 하니까 되긴 했다. 그래서 OPAMCURL
환경 변수를 설정해줬는데(`export OPAMCURL=curl --cacert
/home/me/.cert`), `$OPAMCURL
https://opam.ocaml.org/1.2.2/urls.txt`하면 잘 되는데 `opam update`만
하면 다음과 같은 에러 메시지가 떴다.

> Command "curl --cacert /home/me/.cert" contains 1 space


공백 있는게 대체 왜..? 이해할 수 없는 메시지라 다른 방법을 시도했다.
일단 certificate 오류인건 알았으니 글로벌 environment에서 ca-cert를
먹이면 될 것 같다.  `/usr/share/ca-certificates/` 에 *.crt 파일을
추가하고, `sudo dpkg-reconfigure ca-certificates` 및 `sudo
update-ca-certificates`로 변경 사항을 업데이트 해줬더니 잘됐다. 문제
해결.

근데 대체 왜 되다가 안됐던건지는 아직도 의문이다...
