
//callback when all callbacks have been completed.

module.exports = function (cb) {
  var count = 0, err = null
  return function () {
    count ++
    return function () {
      if(--count) return
      cb()
    }
  }
}

