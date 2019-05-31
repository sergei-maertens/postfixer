Maykin .scss stdlib
===

## Usage
please import libraries explicitly from within your component's `.scss` file:

```scss
@import '../../lib/color';
```

Then use one of the exposed mixins/variables inside your project (note: always scope constants!):

```scss
@import '../../lib/color';

$component-name-color-yellow: $color-yellow;

.component {
  @include color-background();
  color: $component-name-color-yellow;
}

```

## Do not edit
Please see [DO_NOT_EDIT.md](DO_NOT_EDIT.md) for more information.
