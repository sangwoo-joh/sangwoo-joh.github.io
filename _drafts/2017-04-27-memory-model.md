---
layout: post
published: true
title: Memory Model for OCaml
categories: ocaml
---

더 좋은 코드를 쓰기 위해 언어의 내부 표현 구조를 살펴 보는 것은
비싸지만 항상 옳은 일이다. 예를 들어, 실행 도중 메모리가 어떻게
할당되는지를 분석하는 프로파일링 도구를 활용한다던가, 바이너리 파일을
디버거로 실행한다던가 하는데 유용하다. 다행히도 OCaml의 툴체인은 아주
뻔한데, 덕분에 컴파일러가 부리는 최적화 마법을 최소화하고 대신 간단한
실행 모델로 좋은 성능을 얻을 수 있다. 더 좋은 OCaml 코드를 작성하기
위해 메모리 구조를 정리해 둔다.

## OCaml 블록과 값

블록이란 **메모리(RAM)위에 올라가는 연속된 WORD**를 말한다. x86에서는
1 WORD가 4byte(32bit), x86-64에서는 8byte(64bit)이니 대충 감이
온다. 이런 WORD를 연속으로 메모리에 할당하여 블록을 만들고 여기에
튜플, 레코드, 클로저, 배열같은 데이터를 저장한다. OCaml에서는 이런
값이 만들어질 때 메모리 블록을 몰래 할당한다. 타입 선언 자체는 실행
도중에 아무런 메모리를 차지하지 않는다. `let` 바인딩이 있을 때
컴파일러는 적절한 메모리 블록을 실행 도중에 할당하도록 한다.

OCaml은 일관된 메모리 표현 방식을 사용해 모든 변수를 **값(value)**으로
저장하여 관리한다. 하나의 값(스택)은 정수이거나 다른 메모리를 가리키는
포인터 둘 중 하나다.

공식 문서에는 value를, 내가 생각하기에, 두 가지 용도를 혼용해서 쓰고
있다. 하나는 스택 메모리에 올라가는 WORD가 담고 있는 값으로, 앞서 말한
정수/포인터 중 하나이다. 다른 하나는 스택의 WORD가 담고 있는 포인터가
가리키는 힙 메모리 블록에 담겨 있는 OCaml value, 즉 OCaml 데이터
구조로, 정수 뿐만 아니라 튜플, 레코드 같은 복잡한 타입의 값을
말한다. 여기서는 이 두 가지를 구분하기 위해 전자는 *값*, 후자는
*value*로 설명한다.

### 뱀발 1 - 정수와 포인터 표현

OCaml은 대표적인 메모리 재활용(가비지 콜렉션) 언어인데, 실행 도중 모든
값을 추적해서 더 이상 쓸모 없으면 메모리에서 해제해버린다. OCaml은
값의 WORD 중 비트 하나를 이용해서 정수와 포인터를 구분한다. 최하위
비트가 1이면 정수, 0이면 포인터이다. 불리언, 정수, 빈 리스트, unit,
생성자 없는 variant(enumerable) 등 몇 가지 기본 타입이 이 정수 표현을
따라간다. 그래서 OCaml이 x86에서 표현할 수 있는 정수의 범위는 $$0 \sim
2^{31}-1(-2^{30}\sim 2^{30}-1)$$이다.

보통 정수 같은 기본 타입을 추가적인 메타데이터와 함께 감싸서 다른
데이터 구조에 저장하는 걸 **박싱(boxing)**이라고 한다. 데이터를
박싱해서 힙에 올리면, GC(가비지 콜렉터)가 일을 하기 쉬워지는 대신,
박싱된 값을 이용하기 위해서 추가적인 연산이 필요해진다. OCaml에서는
모든 정수를 박싱하지 않고 스택에 올리므로, 추가적인 블록 할당 없이
바로 저장할 수 있다. 그래서 레지스터에 있는 다른 함수에 바로 넘길 수
도 있는 등, 하여튼 가장 빠르고 싸게 쓸 수 있는 값이다.

문제는 최하위 비트가 0일 때, 즉 어떤 값이 포인터일 때, 이게 OCaml
값인지(즉 GC가 주시해야 하는 메모리인지) 혹은 시스템 힙의 C 값인지(즉
GC가 다루면 안되는 메모리인지) 하는 것이다. 사실 실행 시스템은 OCaml
값에 할당한 힙 블록만 계속 추적하므로, 방법은 간단하다: 만약 포인터가
OCaml 실행 시스템이 관리하는 힙 덩어리 내부의 값을 가리키면, 그건
OCaml 값이다. 반면 이 힙 바깥을 가리키면, 이건 다른 시스템 자원을
가리키는 C 포인터로 간주한다. (`out_of_heap_tag(1001)`로 구분하는 것
같다.)



## 블록

블록은 힙 할당의 기본 단위이다. 1 WORD 짜리 헤더와 (불투명한) 가변길이
바이트 또는 OCaml value의 배열로 구성된다(아래 그림 참조). 헤더에는
태그 바이트가 있는데, 이걸 기반으로 나머지 데이터를 어떻게 해석할 지
구분한다.

```
+------------------------+---------+----------+----------+----------+----
| size of block in words |  color  | tag byte | value[0] | value[1] | ...
+------------------------+---------+----------+----------+----------+----
 <-either 22 or 54 bits-> <-2 bit-> <--8 bit-->
```


헤더 이후의 데이터는 두 종류이다: 가변길이의 불투명한 바이트이거나
아니면 value의 배열이다. 가변길이 바이트인 경우 GC는 블록을 관리하지
않는다. OCaml value의 배열인 경우에만 내용물을 유효한 값으로 간주하고
메모리 재활용 과정을 밟는다.


- `size`: 블록의 크기를 메모리 WORD 단위로 나타낸다. 32비트에서는
  22비트, 64비트에서는 54비트이다. 그래서 32비트 아키텍쳐에서 OCaml
  문자열이 최대 16MB로 제한된다.
- `color`: GC의 mark-and-sweep 알고리즘에서 쓰인다. 어떤 경우에도
  소스코드에 드러나지 않는다. GC는 나중에 더 다뤄야겠다.
- `tag byte`: 다양한 용도로 쓰인다.
  - 태그 바이트가 `no_scan_tag(251)` 이상이면 해당 블록은 (불투명한)
    가변길이 바이트로 인식되어 GC의 대상이 아니다. `string` 타입이
    대표적이다.
  - `no_scan_tag` 미만인 경우 블록이 담고 있는 value는 OCaml의 정적
    타입에 의해 결정된다. 다음 단락에서 좀더 자세히 설명한다.

## 값

| value                 | 내용                                       |
| --------------------- | ---------------------------------------- |
| `int` , `char` | 최하위 비트가 1인 정수 값 |
| `unit`, `[]`, `false` | `int 0`과 같은 값 |
| `true` | `int 1`과 같은 값 |
| `Foo | Bar` | 0부터 시작해서 증가하는 `int` 값 |
| `Foo | Bar of int` | 생성자가 있는건 박싱되고, 없는건 위와 동일 |
| Polymorphic variant | 인자 개수에 따라 변수 공간을 어떻게 쓸지 다름 |
| 부동소수점 | Double-precision float을 담은 메모리 블록 하나 |
| `string` | WORD 크기에 맞춘 바이트 배열 + 헤더에 길이 명시 |
| `[1; 2; 3]` | `1::2::3::[]` 과 같은 값으로, `[]`은 `int 0`이고 나머지 `h::t`는 태그 바이트 0과 두 인자로 구성된 메모리 블록 하나 |
| 튜플, 레코드, 배열 | 블록이 value의 배열을 담고 있는 값. 튜플, 레코드는 길이 불변이고 배열은 길이가 변할 수 있다. |
| 전부 `float`만 담은 레코드/배열 | 박싱 안된 `float` 값을 담고 있고, 특별한 태그로 분류됨 |

### 정수, 글자, 기타 기본 타입

이 타입들은 박싱 안된채로 효율적으로 저장된다. 다만 최하위 1비트를
정수/포인터 구분 태그 비트로 쓰기 때문에, 그만큼의 정확도를 잃을
뿐이다.

### 튜플, 레코드, 배열(어레이)

튜플, 레코드, 배열은 전부 태그 바이트가 `0`인 블록으로 표현된다. 다만
튜플, 레코드는 크기가 컴파일 시점에 정해지고, 배열은 실행 도중 크기가
변할 수 있다는 점이 다르다.

OCaml의 `Obj` 모듈을 이용하면 메모리 블록이 어떻게 표현되는지 들여다볼
수 있다.

```ocaml
 Obj.is_block (Obj.repr (1,2,3));;
-: bool = true
 Obj.is_block (Obj.repr 1);;
-: bool = false
```

모듈 함수 이름만 봐도 대충 어떤 것인지 짐작할 수 있다. 튜플
`(1,2,3)`의 메모리 표현(`repr`)은 블록이지만, 정수 `1`은 아니다.

### 부동소수점과 배열

OCaml에서 부동소수점은 항상 배정밀도(double-precision)로
나타낸다. 부동소수점 value 하나는 이 배정밀도의 값 하나만을 담은
블록으로 표현된다. 즉, `Obj` 모듈로 확인해보면 다음과 같다.

```ocaml
 Obj.is_block (Obj.repr 1.0);;
-: bool = true
 Obj.tag (Obj.repr 1.0 );;
-: int = 253
 Obj.double_tag;;
-: int = 253
```

코드에 나타나있듯이 부동소수점 `1.0`은 블록이다. 블록의 태그 값은
`253`인데, 이는 예약된 태그 중 하나인 `double_tag`, 즉 배정밀도의
부동소수점을 나타내며, `no_scan_tag(251)`보다 크기 때문에 GC의 대상이
아니다.

이렇듯 부동소수점 값 하나가 메모리 블록 하나로 박싱되기 때문에,
부동소수점 값을 담은 큰 배열을 다루는 것은 박싱 안된 정수의 배열과
비교했을 때 비효율적이다. 그래서 OCaml은 오직 `float` 타입만 담은
레코드/배열을 특별하게 취급한다. 얘네는 블록의 헤더 이후에 value의
배열이 아니라 float의 배열, 즉 아래 그림처럼 값을 저장한다.

```
+---------+----------+----------+----------+----------+----
|  header | float[0] | float[1] | ...
+---------+----------+----------+----------+----------+----
```

이 특별한 경우를 위해 `double_array_tag(254)`를 써서 구분한다.

주의할 것은 *레코드와 배열의 경우에만* 부동소수점 최적화를 한다는
점이다. 부동소수점을 담은 튜플은 하지 않는다.

### Variant와 리스트

생성자가 없는 일반 variant 타입은 사실 C/C++의 enumerable 타입과
같다. OCaml에서도 이런 enumerated variant는 일반 정수로 순서대로
저장된다. `Obj` 모듈로 확인해보면 다음과 같다.

```ocaml
 type t = A | B | C;;
type t = A | B | C
 Obj.is_block (Obj.repr A);;
-: bool = false
 ((Obj.magic (Obj.repr A)) : int);;
-: int = 0
 ((Obj.magic (Obj.repr C)) : int);;
-: int = 2
 Obj.tag (Obj.repr A);;
-: int = 1000
```

`Obj.magic`은 불안전하긴 하지만 강제로 타입 캐스팅을 해준다. 코드에서
보듯이 enumerated variant는 블록이 아니며, 강제로 `int`로 캐스팅했을
때의 값을 보면 0부터 순서대로 값이 할당되었음을 알 수 있다. `tag` 값은
1000으로, 이는 `Obj.int_tag`와 같은 값이다. 즉, 완전히 `int`다. 근데
`tag` 값이 원래 범위인 8비트를 넘는 값인데, 1000이면 `tag` 윗 비트인
`color` 까지 포함한 10비트로 나타낼 수 있는 범위($$2^{10}$$)에 속하고,
값으로 나타내면 `color`는 2진수 11, `tag`는 232가 되는데 아마 정수
블록을 다루기 위한 boilerplate 쯤 되지 않을까. 근데 이러면 스택에도
박싱된 채로 올라가는건가? 아니면 그냥 `Obj` 모듈로 `int`를 구분하기
위한 값인가? 헷갈린다.

생성자가 있는 parameterized variant는 조금 복잡하다. 메모리 블록에
저장되긴 하는데, `tag` 바이트가 0부터 시작해서 증가하는 값을 갖도록
지정된다. 생성자의 타입을 담을 수 있는 만큼 WORD가 블록에 할당된다.

```ocaml
 type t = A | B of int | C of string | D;;
type t = A | B of int | C of string | D
 Obj.is_block (Obj.repr (B 123));;
-: bool = true
 Obj.tag (Obj.repr (B 123));;
-: int = 0
 Obj.tag (Obj.repr (C "asdf"));;
-: int = 1
```

위에서 보듯, 생성자가 있는 variant는 `tag`가 0부터 시작해서 1씩
올라간다. 따라서 각각의 타입 선언이 가질 수 있는 생성자 variant는 대략
240개 정도임을 알 수 있다. 반면, 생성자가 없는 기본 variant는 정수형과
완전히 같기 때문에 정수 최대 범위 만큼의 variant 타입을 선언할 수
있다.

리스트는 위의 두 variant, enumerated variant와 parameterized variant를
써서 아래의 타입으로 표현한 것과 완전히 같다.

```ocaml
 type 'a list = Nil | Cons of 'a * 'a list
```

즉, 앞서 말했듯이 nil(빈 리스트, `[]` ) 은 `int 0`과 같고, 요소 하나는
`tag`가 0이며 현재 value와 이후 리스트를 가리키는 포인터를 저장하고
있다.

### Polymorphic Variant

얘는 컴파일 시점에 정보가 적어서 최적화할 거리가 많지 않기 때문에,
그냥 variant 보다는 당연히 비효율적이다.

Enumerated variant와 마찬가지로 생성자가 없는 enumerated polymorphic
variant 역시 박싱 안된 정수로 저장된다. 단, 이때 저장되는 정수 값은
해당 polymorphic variant의 *이름*을 해싱한 값을 사용한다. 즉, 0부터
시작해서 1씩 증가하는 정수가 아니라, 해싱된 정수 값을 쓴다.

Parameterized polymorphic variant의 경우, `tag` 바이트로는 해시 값을
담기에 부족하기 때문에, 더 많은 메모리로 이 문제를 극복한다. `tag`
0으로 블록을 할당하고, 1 WORD를 더 써서 해시와 실제 값을 담는다.

### 문자열

`string`은 헤더의 사이즈가 문자열의 길이를 WORD 단위로 담고 있는
대표적인 블록이다. `string_tag(252)`는 앞서 말했듯이 `no_scan_tag`
보다 크기 때문에, GC의 대상이 아니다. 블록의 내용물은 실제 문자열의
내용인데, WORD 정렬을 맞추기 위해 아래와 같이 패딩을 추가한다.

```
+---------------+----------------+--------+-----------+
| header        | 'a' 'b' 'c' 'd' 'e' 'f' | '\O' '\1' |
+---------------+----------------+--------+-----------+
                L data                    L padding
```

32 비트 아키텍쳐에서, 패딩은 문자열 길이와 WORD 크기의 나머지 연산으로
구할 수 있다. 이걸 바탕으로 아래 패딩 값으로 WORD 정렬을 한다.

| 문자열 길이 mod 4(WORD 크기) | 패딩 |
| --------------------- | ------------- |
| 0 | `00 00 00 03` |
| 1 | `00 00 02` |
| 2 | `00 01` |
| 3 | `00` |

64비트에서는 당연히 7바이트까지 계산한다.

잘 보면, OCaml 문자열은 NULL 문자열(`\0`)으로 끝나지 않지만, 패딩을
통해 메모리 블록 위에서는 항상 NULL로 끝나도록 한다는 것을 알 수
있다. 그리고, $$(WORD 수) \times sizeof(WORD) - (마지막 패딩 값 + 1)$$
이라는 간단한 수식으로 $$O(1)$$ 복잡도로 문자열 길이를 구할 수 있다. 즉,
위의 예시에서, `string`의 길이는 $$2 \times 4 - (1 +1) = 6$$ 이다.

그리고 이렇게 NULL로 끝나도록 하기 때문에 C 함수에 넘길 때 편하다.

### 뱀발 2 - 실행 도중 타입 정보가 사라지는 이유?

OCaml 소스를 컴파일 하려고 하면, 제일 먼저 소스 코드를 AST로 바꾼 뒤
이 정보를 바탕으로 **타입 체킹**을 한다. OCaml과 같은
**Hindley–Milner(HM)** 타입 시스템에서는, 타입 체킹에 성공한
프로그램은 반드시 올바른 타입이 적용된다는 것이 증명되어 있다. 예를
들어, `print_endline`은 하나의 `string` 인자를 받는데, 타입 체킹은
이를 컴파일 도중 올바르게 확인한다.

따라서 OCaml은 컴파일 시간에 타입에 대한 검증이 끝나므로, 실행
도중에는 이런 정보를 갖고 있을 필요가 없다. 그래서 이후 컴파일
단계에서는, 실행 도중 다형(polymorphic) 값 같은 걸 구분하기 위한
최소한의 부분만 남겨두고, 나머지 타입 정보를 버리거나 최소화할 수
있다. 이건 java나 .NET 프레임워크에 비하면 엄청난 성능 향상이다.


참조: [리얼 월드
OCaml](https://realworldocaml.org/v1/en/html/memory-representation-of-values.html),
[성능과
프로파일링](https://ocaml.org/learn/tutorials/performance_and_profiling.html)
