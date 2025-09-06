var all = require('./')
var after = all(function () {
  console.log('done')
})

function doSomething(n, cb) {
  setTimeout(function () {
    console.log('N', n)
  }, Math.random() * 100)
}

doSomething(1, after())
doSomething(2, after())
doSomething(3, after())
doSomething(4, after())


