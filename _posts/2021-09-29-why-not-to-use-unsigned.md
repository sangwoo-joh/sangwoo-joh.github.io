---
layout: post
published: false
title: unsigned를 쓰지 말아야 할 이유
category: dev
---

 어쩌다가 C의 타입 캐스팅, 특히 `unsigned`와 관련된 걸 찾아보게
 되었는데... 납득이 가긴 하지만 시간이 지나서 보면 100% 헷갈릴 것이기
 때문에 (...) 짧게 기록해둔다.

## Integral Promotion
 `char`, `short` 뿐 아니라 `unsigned`나 `enum` 타입은 expression에서
 `int` 타입으로 승격(promotion)되어서 실제 연산에 쓰인다. 예를 들면,
 binary operation과 bit-shift operation에서 이 타입들이 연산에 쓰이면,
 일단 `int` 형으로 캐스팅되고 나서 계산이 이루어지고 이 `int` 결과
 값을 최종 변수에 담는다.

## Zero/Sign Extension
 메모리 표현이 작은 타입(e.g. `char`)을 더 큰 타입(e.g. `int`)에
 담으려면, 작은 타입에 비어있는 비트를 큰 타입에 맞게 확장해야
 한다. 이때 **부호**에 맞게 채워야 한다. 만약 작은 타입의 값이
 양수라면 그냥 `0`으로 다 채우면 되지만(Zero Extension), 음수라면 2의
 보수법을 따라야 하므로 `1`로 채우게 된다(Sign Extension).

 예를 들어, 10비트 음수 값인 `11 1111 0001` (즉 `-15`)를 16비트에
 담으려면 비어있는 6비트만큼을 모두 `1`로 채워서 `1111 1111 1111
 0001`로 확장해야지만 16비트에서 `-15`를 표현하는 정확한 2의 보수가
 된다.

---

이 두 가지 행동 각각은 납득이 가긴 한다. 하지만 이걸 고려하지 않고
`unsigned`를 마구 쓰다보면 의도치 않은 동작을 일으킬 수 있다.

---

```c
unsigned char p = 0xff;
unsigned long long res = p << 24;
// expected: 0x0000 0000 ff00 0000
// actual  : 0xffff ffff ff00 0000

printf("Expected value: %lu, Actual value: %lu\n", 0x00000000ff000000, res);
// Expected value: 4278190080, Actual value: 18446744073692774400
```

 `p`의 타입이 `unsigned char`이지만, bit-shift 계산을 위해 `int`
 형으로 integral promotion 된다. 그래서 `p << 24`는 `0xff00 0000`를
 담은 32비트 정수값이 되어버린다. 여기까진 좋다.

 하지만 이 최종 값을 `unsigned long long` 타입에 담을 때 sign
 extension이 발생하게 된다. 먼저 `int` 타입의 `0xff00 0000`은 MSB가
 1이므로 2의 보수 표기법에 따라 이를 **음수**로 해석하게 되고, 모자란
 32비트를 모조리 `1`로 채운다. 따라서 결과 값은 `0xffff ffff ff00
 0000`이 되어 버린다. 그 이후 `unsigned`가 적용되므로, `res`의 값은
 엄청나게 큰 값이 되어버린다. 값을 찍어보면 기대했던 `0x0000 0000 ff00
 0000`보다 엄청나게 큰 값을 볼 수 있다.

 현실에서는 이 값이 복잡한 경로(e.g. 입력)로 들어오기 때문에, 곧바로
 확인하기가 어렵다. 거기다 이렇게 들어온 값이 직접 쓰이게 되면 경우에
 따라 *가끔씩* 의도치 않은 동작을 할 수 있어서 더 헷갈린다.

 위의 코드를 좀더 꼬아서 다음과 같은 경우를 생각해보자.


```c
unsigned char p = 0xff;  // maybe from input
unsigned long long k = 0x00000000ff000000; // save correct value
printf("p << 24: 0x%016lx, k: 0x%016lx\n", p << 24, k);
// p << 24: 0x00000000ff000000, k: 0x00000000ff000000
// print the same representation!

if ( (p << 24) > k) {
  printf("You shall not reach here!\n");
}
```

 디버깅을 위해 값을 하나씩 찍어보면, `p << 24`의 값은 `0`이 잘 채워진
 `0x0000 0000 ff00 0000`이 나온다. 그러므로 `(p << 24) > k`의 결과는
 `false`가 되어 브랜치 안의 `printf`에 도달하지 못할 거라는 예측은
 언뜻 그럴듯하다. 하지만 실제로 이 코드를 컴파일해서 실행하면 "You
 shall not reach here!" 메시지가 뜬다. 각각을 출력할 때에는 의도한
 결과가 나왔지만, `(p << 24) > k`를 계산하는 과정에서 sign extension이
 발생하여 의도치않게 저기에 도달하고 만 것이다.

---

 그러니까 결론은, 잘 모르겠으면 그냥 `unsigned`를 쓰지말고, 연산에
 쓰일 모든 변수/값들은 최대한 같은 메모리 표현을 갖는 타입으로
 통일하자, 정도가 되겠다.

 (빠르게 작성하느라 원인을 잘 설명하지 못한 부분에 대한 코멘트는
 언제든지 환영합니다)
