---
layout: post
published: true
title: 나의 개발 프로세스
subtitle: 타입, 그리고 커밋 메시지
category: thoughts
---

 세상에는 소프트웨어를 잘 만들기 위한 다양한 개발 프로세스가
 있다. 아마도 이 중 가장 유명한 것은 TDD, 이른바 테스트 주도 개발
 (Test Driven Development) 일 것이다. 한때 엄청나게 유행이었기도
 했으니까.

 하지만 개인적으로는 TDD가 크게 와닿진 않는다. 자꾸 제품이 아니라
 테스트케이스를 중심에 두게 되는 듯한 느낌이 썩 불편했다. 그리고 내
 이런 생각에 쐐기를 박은 것은 [데이크스트라의 한
 마디](https://www.cs.utexas.edu/~EWD/transcriptions/EWD03xx/EWD340.html)
 였는데, 인용하자면 다음과 같다:

> ... But program testing can be a very effective way to show the
> presence of bugs, but is hopelessly inadequate for showing their
> absence.

 정확한 문장은 처음 읽었는데, 그간 무의식적으로 느꼈던 테스트케이스의
 부족함이 한방에 와닿았다. "절망적으로 불충분" 하다니.

 그렇다면 무엇을 중심에 두고 개발을 해야할까? 더 구체적으로 나는
 이때까지 무엇-주도 개발을 해온걸까? 곰곰이 생각해본 결과 다음 두
 가지로 결론내릴 수 있었다.

## Type
 첫번째는 타입 주도 개발이다. Type Driven Development 이니 이것 역시
 TDD 가 되겠다. 나의 마음 속 구루이신 [끈닷넷](kkeun.net) 형님과 페어
 프로그래밍에서 특히나 이것을 깊게 느낀 것 같다.

 뭔가 개발하는 경우는 보통 두 가지로 나뉘어 진다. 하나는 명확하게 어떤
 값을 만들어내야 하는 경우이고, 다른 하나는 사이드이펙트를 만들어내야
 하는 경우이다.

 값을 만들어야 하는 경우, 타입 주도 개발은 명쾌하다. 이 값에는 상수나
 변수 뿐 아니라 함수, 모듈 등이 포함된다. 내가 어떤 타입의 값을 만들어
 내야 하는지를 고민하다보면 자연스럽게 타입을 먼저 생각하게 된다.

 사이드이펙트를 만들어내야 하는 경우는 명시적으로 값을 리턴하지 않아도
 되기 때문에 조금 헷갈렸었다. 개인적으로 이때는 "만들어낸
 사이드이펙트에 대한 리포트"를 리턴 타입으로 염두에 두고 개발한 것
 같다. 그래야 방향을 잃지 않았다.

 이런 타입-주도 개발은 개인적으로는 프로덕트 개발 초기에, 프로그램이
 제대로 동작할지 말지 모르는 깜깜한 상황에서 방향을 잃지 않고 끝까지
 갈 수 있었던 원동력이라고 생각한다. 여기에는 경험적인 근거도 있다.

 이 프로세스는 특히 논리적으로 탑 다운 방식이다. 프로그램은 (불변의)
 값으로 이루어져 있고, 이 값들은 변수나 상수, 혹은 함수가 될 수
 있다. 특히 함수의 경우는 어떤 함수를 작성할지가 아니라, 최종적인
 값(목표)을 만들기 위해서는 *어떤 함수를 사용하면 좋을지*를 먼저
 고민한 뒤에, 그 함수의 타입 시그니쳐를 생각해서 "이런 타입을 리턴하는
 함수가 있으면 좋겠군" 을 가정하고 코드를 작성할 때, 생산성이 좋았던
 경험이 있다.

## Commit Message
 두번째는 커밋메시지 주도 개발이다. 이건 한때 트위터에서도 유행이었던
 것이긴 한데, 생각해보니 나도 모르게 이짓을 하고 있었던 것 같다.

 일전에 [커밋 메시지와 관련된
 포스팅](https://sangwoo-joh.github.io/commit-message)을 쓰기도
 했는데, 여기서도 커밋 메시지가 곧 작은 작업의 단위임을
 가정했었다. 즉, 코드를 짜고 나서 커밋을 하는게 아니라, 커밋 메시지에
 무엇을 적을지를 먼저 고민하고 그 후에 코드 작성에 착수하는, 궁극의
 탑-다운 방식이다.

---

 물론 이 두 가지 프로세스가 무조건 옳다는 것은 아니다. 그저 "내가
 해봤더니 방향을 잃지 않고 개발하는데 도움이 되더라" 로 봐주자. 거기다
 이렇게 한다해도 테스트케이스 없이 개발을 진행할 순 없다. 특히
 positive보다는 negative 테스트케이스가 더 중요하더라.

 그래도 저 두 가지를 마음에 갖고 있으면, 지금 당장 눈에 보이는
 동작하는 프로그램이 없더라도 안심하고 개발할 수 있다. 다른 사람들은
 어떤-주도 개발을 하는지 궁금하다.