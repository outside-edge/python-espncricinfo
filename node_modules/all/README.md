# all

callback when all callbacks have fired.

<img src=https://secure.travis-ci.org/dominictarr/all.png?branch=master>

``` js
var all = require('all')
var after = all(function () {
  console.log('done')
})

function doSomething(n, cb) {
  setTimeout(function () {
    console.log('N', n)
  }, Math.random() * 100)
}

doSomething(1, cb())
doSomething(2, cb())
doSomething(3, cb())
doSomething(4, cb())

```


## License

MIT
