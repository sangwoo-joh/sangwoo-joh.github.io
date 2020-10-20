---
layout: post
published: true
title: OCaml Module and Functor
categories: ocaml
---

## 모듈

### 기본

OCaml은 모든 소스 파일을 모듈로 취급한다. 이때 자동으로 파일명의 첫
문자가 대문자로 바뀐 모듈로 인식한다. 예를 들어 `duck.ml`이라는 파일을
작성하면, 다른 파일에서는 `Duck.foo ()` 형태로 해당 모듈(예시의 경우
`foo` 함수)에 접근할 수 있다. 또는 키워드를 사용해서 `open Duck` 와
같이 해당 모듈을 전방위로 불러올 수도 있다. 이런 점에서, OCaml의
모듈은 객체지향 모델에서의 클래스나 네임스페이스와 그 역할이 비슷하다.

### 인터페이스

이렇게 모듈을 작성하고 나면, 특별한 일을 하지 않는 이상 모듈 내의 모든
내용 -함수, 타입, 서브모듈 등- 이 공개된다. 이는 객체지향에서 모든
멤버들을 `public` 키워드로 작성한 것과 같다.

OCaml은 이런 접근성을 조절하기 위해 인터페이스를
제공한다. 인터페이스는 모듈의 구현 중 공개하고 싶은 것만을 적어둔
것으로 `.mli` 확장자를 갖는다. 다시 말해, 모듈의 타입이 곧
인터페이스인 것이다. 따라서 `val` 키워드로 모듈의 껍데기를 보여줄 수
있다.

#### Abstract type: 추상 타입

추상 타입과 요약 타입 중 뭐가 더 괜찮은 번역인지는 모르겠다. 일단
'추상적'이라는 단어 자체의 뜻이 잘 와닿지 않기 때문에 '요약'이라는
번역도 괜찮은 듯하지만, 사전적 의미를 찾아보니 다음과 같았다.

> 추상-적
>
> 1. 어떤 사물이 직접 경험하거나 지각할 수 있는 일정한 형태와 성질을 갖추고 있지 않은, 또는 그런 것.
> 2. 구체성이 없이 사실이나 현실에서 멀어져 막연하고 일반적인, 또는 그런 것.

둘 중 2번의 의미가 abstract type의 번역에 매우 적절하다는 느낌을
받았다. 따라서 이 글에서는 '추상 타입'으로 표기하려고 한다.

아무튼간에 인터페이스에서, 함수나 상수 같은 값(value)은 `val` 키워드로
보여줄 수 있었다. 타입의 경우는 어떻게 할까? 특히 모듈은 새로운 타입을
자주 정의한다. OCaml 홈페이지에 나온 간단한 레코드 타입의 예시를 보자.

```ocaml
type date = { day : int, month : int, year : int }
```



여기서 `.mli` 파일을 작성할 때 가능한 옵션은 무려 4가지나 된다.

1. 인터페이스(시그니쳐)에서 타입을 완전히 생략한다.(=private)
2. 타입 정의를 시그니쳐에 복붙한다.(=public)
3. 타입의 이름만 줘서 **추상 타입**으로 만든다.
4. 레코드 타입의 필드를 읽기 전용으로 만든다: `type date = private { ... }`(=Get())

여기서 1, 2, 4번은 명확하니 넘어가고, 3번의 추상 타입의 경우를 조금 더
살펴보자. 이 경우 인터페이스에는 다음의 코드 한 줄만 작성한다: `type
date`

이렇게 하면, 사용자는 `date `타입이 존재한다는 걸 알 수 있고 이 타입의
객체를 함수로 다룰 순 있지만, 해당 레코드 타입의 필드는 알 수
없다. 즉, `date`에 `day`가 있는지도 알 수 없고, `date.day`같은 짓은
당연히 할 수 없다.  따라서 해당 모듈이 제공하는 함수만을 통해서 `date`
객체를 다루어야 한다. 예를 들어서 이 모듈이 다음과 같은 3 가지 함수를
제공한다고 하자.

```ocaml
type date
val create : ?days:int -> ?months:int -> ?years:int -> unit -> date
val sub : date -> date -> date
val years : date -> float
```

요점은 `create`와 `sub` 함수를 통해서만 `date` 타입 데이터를 만들 수
있다는 점이다. 즉, 모듈의 사용자가 ill-formed(부적절한 모양의)
레코드를 만들 수가 없다. 이를 통해서 얻을 수 있는 이점은
상당하다. 특히 라이브러리를 작성할 때 버전이 올라가도 같은
인터페이스를 제공하면, 데이터 구조(예시의 경우 `date` 레코드)를 포함한
내부 구조를 마음껏 바꿀 수 있다. 그리고 사용자는 이걸 알 수도 알
필요도 없다.

### 서브모듈

파일에 코드를 작성해서 해당 파일명의 모듈을 만들 수도 있지만, `module`
키워드로 파일 내에 서브모듈을 작성할 수도 있다. 이같은 점 때문에
서브모듈 역시 객체지향의 네임스페이스와 매우 유사하다. 서브모듈의
인터페이스 역시 작성할 수 있는데, 이를 모듈 타입(시그니쳐)이라고
한다. 예를 들면 다음과 같이 `Woo` 모듈을 작성할 수 있다.

```ocaml
module Woo : sig
  val duck : unit -> unit
end =
struct
  let penguin = "penguin"
  let duck () = print_endline penguin
end
```



위 코드는 아래와 같이 `mli/ml` 파일에 나누어 작성하는 것을 추천한다.

```ocaml
(* in mli *)
module type Woo_type : sig
  val duck : unit -> unit
end

(* in ml *)
module Woo : Woo_type = struct
  ...
end
```

여기서 `Woo_type`은 모듈 타입에 이름을 붙인 것이고, 다른 모듈
인터페이스를 정의할 때 재사용할 수 있다.

## 펑터

여기까지 알아본 모듈은 그 자체로도 쓸만하지만, **펑터(Functor)**를
통해 그 쓰임새가 분명해진다. 그리고 이 글을 쓰는 이유이기도
하다. 뱀발로, Functor는 보통 '함자' 혹은 '함수자'로 많이들 번역하는데,
Function이 '함수'로 번역되는걸 생각하면 그리 나쁘지 않은 번역인 것
같긴 하다. 하지만 '펑터'라고 읽는 쪽이 훨씬 찰지기 때문에, 이 글에서는
굳이 '함자'나 '함수자'라는 번역을 쓰기보다는 '펑터'로 표기하려고 한다.

아마도 OCaml에서 가장 복잡한 특징 중 하나가 이 펑터일 것이다. 나 역시
초기에 펑터를 많이 쓰는 코드를 읽는데 어려움을 겪었다. 하지만 펑터를
잘 쓰면 정말로 코드가 아름다워진다. 이 글은 [Ocaml 공식
홈페이지](https://ocaml.org)의 모듈 부분과 [Inria의 OCaml
매뉴얼](https://caml.inria.fr/pub/docs/manual-ocaml/moduleexamples.html),
그리고 [코넬 대학의
렉쳐노트](http://www.cs.cornell.edu/courses/cs3110/2011sp/Lectures/lec09-functors/functors.htm)를
참조했다.

### 왜 필요한가?

간단히 말해 펑터는 모듈에서 모듈로 가는 함수라고 할 수 있다. 함수가
어떤 값(인자, argument)으로 매개변수화 된(parametrized) 값이라면,
펑터는 어떤 모듈로 매개변수화 된 모듈인 것이다.

무엇보다도, 펑터는 타입을 값으로 매개변수화 할 수 있는데, 이건 OCaml이
직접적으로는 제공하지 않는 기능이다. 이건 마치 C++의 템플릿이나 자바의
제네릭 타입과 비슷한 역할을 한다. 예를 들어서, 정수 n을 받아서 딱 길이
n 짜리 배열과 이 배열에만 동작하는 함수를 내놓는 펑터가 있다고
하자. 만약에 사용자가 이 모듈에 일반적인 가변 길이 배열을 넘겨도
*컴파일 에러*가 뜬다. 이렇듯 펑터는 올바른 코드를 작성하기 위해
존재한다.

다만 한가지 알아둬야 할 것은, 펑터가 성능을 올려주기 위해 만들어진
것이 아니라는 점이다. 펑터는 **코드를 올바르게 작성하기 위해**
만들어진 것이다. 심지어 `ocamldefun`같은 defunctorizer(뭐라고
번역해야할 지 모르겠다..)를 쓰지 않으면 런타임 성능이 떨어지기도
한단다. 이건 나중에 알아보도록 하고 일단 펑터가 뭔지 살펴보자.

### 어떻게 정의하나?

인수가 하나인 펑터는 다음과 같이 정의한다.

```ocaml
module F (X : X_type) = struct
  ...
end
```

모듈 정의와 거의 비슷하다. 여기서 `X`는 인자로 넘겨질 모듈이다.
`X_type`은 그 모듈 타입(시그니쳐, 인터페이스)이고 반드시
필요하다. 이게 없으면 대체 어떤 타입의 모듈을 다룰 수 있는지 알 길이
없기 때문이다.


또 다음과 같이 펑터가 리턴하는 모듈의 시그니쳐(모듈 타입)을 강제할
수도 있다. 마치 함수의 타입을 적는 것과 비슷하다.

```ocaml
module F (X : X_type) : Y_type = struct
  ...
end
```


역시 `.mli` 파일에 다음과 같이 추상적으로 드러낼 수 있다. 마치
인터페이스에서 함수나 상수의 타입만 드러내는 `val` 키워드와 같은
역할을 한다.(`module type`이 아니다!)

```ocaml
module F (X : X_type ) : Y_type
```



또는 아예 `functor`라는 키워드를 써서 작성할 수도 있다.

```ocaml
module F = functor ( X : X_type) ->
struct
  ...
end
```

이건 마치 함수를 정의할 때 `let f (x:int) = x+1`로 쓰느냐 `let f = fun
(x:int) -> x+1`로 쓰느냐 하는 문제와 비슷하다. 함수를 정의할 때는 타입
추론을 해주기 때문에 인자로 받는 `x`의 타입을 명시할 필요가 없다는
점만 빼면 말이다. 어찌됐든 확실히 `functor`라는 키워드를 드러냈을 때
그 의미가 더 명확해지는 것 같긴 하다.

아마도 이 문법 자체가 잘 와닿지 않았던 것 같다. 객체지향에서 상속
키워드였던 `:`가 함수형에서 타입 정의인 것도 어색한데, 모듈에
타입이라니? 하지만 이는 OCaml의 중요하고 아름다운 기능이고, 소스를
계속 보다보니 결국 익숙해져서 지금은 아주 깔끔한 문법이라고 생각한다.

### 펑터와 추상 타입

앞에서 나왔던 추상 타입을 펑터 내부에 적용하여 실제 구현을 가리는 것이
현실에서는 더 좋다. 집합을 내놓는 펑터가 있을 때, 실제 내부 구현이
무엇인지 사용자는 알 필요가 없으며, 나중에 적절히 구현을 바꿀 수 있는
좋은 명분이 되기 때문이다.

마찬가지로 적절한 펑터 시그니쳐 키워드로 작성하면 된다.

```ocaml
module type F_Type = functor (X : X_type) -> sig
  ...
end
```

### 예시

개념을 단단하게 이해하기 위해서는 역시 그 쓰임새가 중요하다. 예시를 보자.

집합 모듈 `Set`을 구현해보자. 파일 이름은 `set.ml`이 될 것이고 집합이
담을 요소들은 그 타입이 무엇이 됐든 **서로 비교**할 수만 있으면 될
것이다. 그리고 이런 비교할 수 있는 모듈을 받아서 실제 집합 모듈을
내놓는 펑터 `Make`를 만들자. 자세히 말하면, `Set` 모듈 내부의
`Make`라는 **펑터**는 **서로 비교**할 수 있는 모듈 타입
`OrderedType`의 모듈을 받아서 해당 모듈을 담는 집합 모듈 타입 `S`의
모듈을 내놓는 함수(펑터)이다.

일단 **비교**할 수 있는 모듈 타입 `OrderedType`부터 정의하자.

```ocaml
module type OrderedType = sig
  type t
  val compare : t -> t -> int
end
```

아주 깔끔하다. `compare`는 두 `t` 타입의 인자를 비교해서 작으면 음수,
같으면 0, 크면 양수를 리턴하면 된다. 만약 집합의 정렬 순서를 반대로
하고 싶다면 반대의 값을 리턴하면 될 것이다. 시그니쳐 `OrderedType`은
어떤 임의의 타입 `t`에 대해서 서로 비교할 수 있는 `compare`함수만 갖고
있으면 된다는 의미이다.

이제 이 `OrderedType` 모듈 타입을 담는 집합 모듈 타입 `S`를
정의해보자. 즉, `Set` 모듈이 실제로 리턴하는 모듈의
타입(시그니쳐)이다. 사실 해당 집합 모듈을 내놓는 펑터를 바로 정의해도
되지만 더 정확한 이해를 하는데 도움이 된다. (실제 구현에서는 아래와
같은 시그니쳐를 펑터의 리턴 모듈 타입으로 그냥 쓰면 **안된다**. 이유는
아래 참조.)

```ocaml
module type S = sig
  type elt
  type t
  val empty : t
  val add : elt -> t -> t
  val mem : elt -> t -> bool
end
```

온전한 집합을 만들기 위해 더 많은 연산을 추가해도 되겠지만 편의를 위해
필수적인 간단한 연산만 추가했다. `elt`는 집합 요소(element)의
타입이고, `t`는 집합 자체의 타입이다. `empty`, `add`, `mem`은 각각 빈
집합 상수, 요소 추가 함수, 요소 존재 확인 함수로 문자 그대로의 값이다.

이제 진짜 펑터를 만들어보자. 실제 구현은 밸런스 트리로 되어있지만,
편의를 위해 그냥 리스트로 구현했다.

```ocaml
module Make(Ord : OrderedType) = struct
  type elt = Ord.t
  type t = elt list
  let empty = []
  let rec add x s =
    match s with
    | [] -> [x]
    | hd::tl ->
      if Ord.compare x hd = 0 then s
      else if Ord.compare x hd < 0 then x::s
      else hd::(add x tl)
  let rec mem x s =
    match s with
    | [] -> false
    | hd::tl ->
      if Ord.compare x hd = 0 then true
      else if Ord.compare x hd < 0 then false
      else mem x tl
end
```

실제 라이브러리는 역시 파일(모듈) 이름이 `set.ml`인 모듈 안에
`Make`라는 펑터로 정의되어 있어서, `Set.Make(OrderedData)`와 같이 만들
수 있다. 꽤 아름다운 문법이라고 생각한다.

`elt`는 당연히 파라미터로 받은 비교 가능한 모듈과 같은 타입이 되어야
하고, 집합 자체의 타입은 리스트로 정의했다. 나머지 함수들은 요소가
중복없이 순서대로 채워질 수 있도록, `elt` 즉 `Ord`의 함수인
`Ord.compare`를 호출하여 처리했다. 나무랄 데 없다.

이렇게 만들고 나면 다음과 같이 쓸 수 있다.

```ocaml
module OrderedString = struct
  type t = string
  let compare x y = if x=y then 0 else if x<y then -1 else 1
end

module SetOfString = Set.Make(OrderedString) (* Set 생성 *)
SetOfString.mem "duck" (SetOfString.add "penguin" SetOfString.empty) (* false *)
```

`OrderedType` 시그니쳐와 같은 타입의 `OrderedString` 모듈을 정의하고
`Set.Make` 펑터를 호출하여 문자열의 집합을 만들었다. 그리고 만들었던
세 가지 연산을 모두 사용해봤다. 아주 잘된다.

### 미묘한 점 1

예시에서 `OrderedString` 모듈을 구현할 때, `OrderedType` 시그니쳐를
명시하지 않았다. 즉, 아래와 같이 코드를 적지 않았다.

```ocaml
module OrderedTypeString : OrderedType = struct
  ...
```

이게 객체지향 관점에서 보면 마치 `OrderedType`이라는 virtual 클래스를
상속받아서 구현하는 것처럼 보여서 꽤 괜찮은 생각 같지만 실제로는
그렇지 않다. 저렇게 명시해서 구현한 `OrderedTypeString`으로 `Set.Make`
펑터를 호출하면 다음과 같은 오류를 뱉는다.

```ocaml
## module WrongSet = Set.Make(OrderedTypeString);;
## let s = WrongSet.add "yikes" WrongSet.empty;;
                       ^^^^^^^
Error: This expression has type string but an expression was expected of type WrongSet.elt = OrderedTypeString.t
```

string 타입이라는 것도 추론이 되었고 모든게 성공적일 거라 생각했지만,
에러를 뱉는 이유는 뭘까? 이는 시그니쳐 `OrderedType`으로 인해 내부
타입 정의인 `type t = string`을 드러내지 않기 때문이다. 즉, 시그니쳐의
`type t`로 인해 앞서 말했던 **추상 타입**으로 선언됐기 때문에, 펑터가
이 정보를 공짜로 사용할 수 없는 것이다. 오직 `OrderedTypeString`
모듈만을 통해서 `type t`가 다뤄질 수 있다. 생각해보면 이건
당연하다. 그래서 펑터는 `OrderedTypeString.t` 가 실제로 `string`인지
모른채로 모듈 `WrongSet`을 만들어낸 것이다. 마지막으로
`WrongSet.elt`에 `OrderedTypeString.t`를 담으려고 하지만, 이 둘의 타입
이퀄리티를 `OrderedTypeString` 모듈 없이는 확인할 수 없기 때문에 타입
체커에서 실패한다.

반면 앞서 예제 처럼 `OrderedType` 시그니쳐를 생략하면, OCaml은 다음과
같이 모듈 타입을 추론한다.

```ocaml
## module OrderedString = struct
  type t = string
  let compare x y = if x=y then 0 else if x<y then -1 else 1
end;;
module OrderedString :
  sig
    type t = string
    val compare : string -> string -> bool
  end
```

코드 조각에서 보듯이, `type t = string`이 **드러나있고**, 따라서
펑터가 해당 정보를 알 수 있어서- 타입 체커를 통과한다. (`S.elt =
OrderedString.t`)

### 미묘한 점 2

추상 타입을 이용하면 아래와 같이 펑터의 내부 구현을 가릴 수 있다.

```ocaml
module type AbstractMake = functor (Ord : OrderedType) -> sig
  type elt = Ord.t
  type t (* abstract *)
  val empty : t
  val add : elt -> t -> t
  val mem : elt -> t -> bool
end

module AMake = (Make : AbstractMake)
module AbstractStringSet = Set.AMake(OrderedString)
AbstractStringSet.add "duck" AbstractStringSet.empty (* AbstractStringSet.t = <abstr> *)
```

정의한 `Make`의 시그니쳐 `AbstractMake`를 만들어서 `AMake`라는 펑터가
해당 시그니쳐를 강요하도록 했기 때문에, 실제로 잘 동작하는 코드이고
내부 구현도 드러나지 않는다. 즉, `<abstr>`타입으로 추론됨을 알 수
있다. 여기까진 괜찮다.

하지만 조금 더 생각해보면, 타입을 더 우아하게 가리기 위해서 펑터가
리턴하는 모듈 타입 역시 시그니쳐로 제한하고 싶어진다. 다음과 같이
말이다.

```ocaml
module type S = sig
  type elt
  type t
  val empty : t
  val add : elt -> t -> t
  val mem : elt -> t -> bool
end

module WrongMake = (Make : functor(Ord : OrderedType) -> S)
```

여기서 `S`는 위의 집합 모듈의 자체의 시그니쳐이다. 펑터의 추상 타입을
이용한 것과 다른 점은, 이 구현에서는 리턴하는 모듈 타입의 `elt` 타입의
정보를 잃었다는 점 뿐이다. 즉, `AbstractMake`에 있던 `type elt =
Ord.t`라는 정보를 잃었다. 그래서 이 코드는 이전과 같은 이유로 인해
오류를 뱉는다.

```ocaml
## module WrongStringSet = WrongMake(OrderedString);;
## WrongStringSet.add "yikes" WrongStringSet.empty;;
                     ^^^^^^^
Error: This expression has type string but an expression was expected of type WrongStringSet.elt = WrongSet(OrderedString).elt
```

역시 문제는 시그니쳐 `S`로 인해 `elt` 타입이 추상 타입이 됐기 때문에,
펑터가 뱉은 `WrongStringSet.elt` 타입과 파라미터로 받은
`OrderedString.t`의 타입 이퀄리티를 알 수 없다는 점이다. 결과적으로
`WrongStringSet.elt`이 `string`타입인지 알 수 없어서, `WrongStringSet`
모듈의 함수를 `string`에 적용할 수 없게 된다.

아쉽게도 위와 같은 문맥에서는 `S`를 정의할 때 `Ord.t` 정보를 알 수
없다. 하지만 OCaml은 갓-언어이기 때문에 `with type` 키워드를 통해
추가적인 타입 이퀄리티 조건을 시그니쳐에 추가할 수 있다.

```ocaml
module Make (Ord : OrderedType) : S with type elt = Ord.t
```

혹은 아래와 같이 써도 된다.

```ocaml
module AMake = (Make : functor(Ord: OrderedType) -> (S with type elt = Ord.t))
```

이렇게 하면 타입 체커를 위한 타입 이퀄리티 정보를 끼워넣을 수 있어서
모든 일을 순조롭게 진행할 수 있다.

### 정리

OCaml의 가장 복잡하지만 중요한 기능인 펑터에 대해서 알아봤다. 웬만한
오픈소스들이 펑터를 통해 기능을 제공하고 있기 때문에 깊이 알아둘
필요가 있었다. 그리고 더 깊은 이해를 위해서 실제 라이브러리 구현을
보고 있는데, 생각보다 재밌다. 특히 핵심이라고 할 수 있는 `set`과 `map`
모듈의 구현은 읽는 맛이 있다. 앞으로도 종종 재밌는 내용을 올리고 싶다.
