Udon Memo
====

## Restriction on variable initialization in .data segment

Initialization of variables in the .data segment is possible
Integer, float, and string types only.

OK
``` 
        __const_3: %SystemInt32, 0
        ret_addr: %SystemUInt32, 0xFFFFFF
        __const_1: %SystemSingle, 1.0
        __const_6: %SystemString, "Renderer"
```

NG
```
        __const_2: %SystemBoolean, true # null only
```

## Udon instruction byte code size

### 1byte
nop, pop, copy

### 5byte
push, jump_if_false, jump, extern, jump_indirect

## Avoid restrictions on variable initialization

If you use [type name].Parse ([string representing a constant]),
you can initialize anything other than int, float, and string.

```
        __const_39: %SystemBoolean, null
...
        PUSH, "true"
        PUSH, __const_39
        EXTERN, "SystemBoolean.__Parse__SystemString__SystemBoolean"

```

