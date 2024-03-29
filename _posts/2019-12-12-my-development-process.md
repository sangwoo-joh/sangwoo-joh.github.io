---
layout: post
tags: [dev, think]
published: true
title: 나의 개발 프로세스
last_update: 2024-03-27 11:58:58
---

 세상에는 소프트웨어를 잘 만들기 위한 다양한 개발 프로세스가 있다. 아마도 이 중 가장 유명한 것은 TDD, 이른바 테스트 주도 개발 (Test Driven Development) 일 것이다. 하지만 개인적으로는 TDD가 크게 와닿진 않는데, 특히 [데이크스트라의 한 마디](https://www.cs.utexas.edu/~EWD/transcriptions/EWD03xx/EWD340.html)의 영향이 컸다.

> ... But program testing can be a very effective way to show the presence of bugs, but is hopelessly inadequate for showing their absence.

 그럼에도 불구하고 테스트는 반드시 필요하다. 특히나 컴파일러가 없는 동적 타이핑 언어로 개발할 때는 더더욱 그렇다. 테스트는 버그가 *없음*을 보여주기 위한 용도라기 보다는, *최소한의 제약 조건*을 실행 가능한 코드로 작성해두었다는 데에 의의를 두어야 한다고 생각한다.

 반면 내가 테스트보다 조금 더 중점을 두는 것은 바로 타입이다.

## Type
 기본적으로 우리가 만드는 소프트웨어는 무언가를 계산하기 위한 것이다. 애초에 컴퓨터라는 단어부터가 Compute 에서 나오기도 했고, 전산학 이론에서 주로 다루는 내용 중 하나가 "계산"에 대한 내용이기도 하다. 즉, 우리가 만드는 **모든** 소프트웨어의 중심에는 계산이라는 목적이 있고, 이는 자연스럽게 타입과 연결된다.

 프로그램은 보통 함수들로 이루어진다. 함수는 크게 두 가지로 나눌 수 있다. 하나는 특정한 *종류*의 값을 계산하는 것이고, 다른 하나는 사이드이펙트(파일에 쓰기, 콘솔에 쓰기, non-deterministic한 계산 등)를 만들어 내는 것이다.

 값을 계산하는 경우는 분명하다. 이 값에는 상수나 변수 뿐 아니라 함수, 모듈 등이 포함된다. 내가 어떤 타입의 값을 만들어 내야 하는지를 고민하다보면 자연스럽게 타입을 먼저 생각하게 된다. 그리고 동적 혹은 정적 타이핑 언어에 상관없이 이 타입을 명시적으로 적어주는 것은 이후에 코드를 읽는 데에 크게 도움이 된다.

 사이드이펙트를 만들어내야 하는 경우는 조금 헷갈린다. 명시적인 리턴 값이 없고 보통은 `Unit` (또는 `void`) 타입을 리턴하기 때문이다. 이런 함수는 되도록 주의 깊게 작성하고 나중에 읽었을 때에도 최대한 잘 읽힐 수 있게 네이밍이나 함수 길이에 신경쓰면서 작성하게 된다.

 이런 타입-주도 개발은 개인적으로는 프로덕트 개발 초기에, 프로그램이 제대로 동작할지 말지 모르는 깜깜한 상황에서 방향을 잃지 않도록 하는 원동력이 된다고 생각한다. 논리적으로는 탑 다운 방식이라고 볼 수 있다. 프로그램은 값들로 이루어져 있고, 이 값들은 변수나 상수, 혹은 함수가 될 수 있다. 프로그램의 의도를 생각했을 때, 프로그램이 계산하고자 하는 최종적인 값(목표)을 위해서 필요한 함수들을 쪼개어 생각하다 보면 프로그램이 모듈 방식으로 잘 구성되는 경험을 하기도 했다. 예를 들어서, "이런 타입의 값을 계산하는 함수가 있다고 가정하고" 이 함수를 이용해서 한 단계 씩 프로그램을 구성하다 보면 자연스럽게 모습을 드러내는 것이다.

 그리고 (특히 동적 타이핑 언어에서) 타입을 잘 적어두면, 나중에 다시 돌아와서 코드를 읽을 때 정말 큰 도움이 된다. 변수나 함수 이름만 봐서는 어떤 종류의 값을 계산하는지 알기 힘든 경우가 많은데, 이때 타입 어노테이션이 있으면 프로그램을 이해하기 위한 올바른 멘탈 모델을 만드는 데에도 큰 도움이 될 뿐만 아니라, IDE의 Jump to Definition 기능이 활성화 되기 때문에 실제로 타입을 정의한 구체적인 코드를 찾는데에도 도움이 된다.
