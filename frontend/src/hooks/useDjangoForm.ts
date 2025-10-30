// load form

type DjangoFormErrors = {
  [fieldName: string | "__all__"]: string[]
}

type DjangoForm = {
  next?: string // a Django `next` param
  errors?: DjangoFormErrors
}

function attachErrors(form: DjangoForm) {
  const errorsEl = document.getElementById("form-errors-json")
  if (errorsEl && errorsEl.textContent.startsWith("{")) {
    let errors = null
    try {
      errors = JSON.parse(errorsEl.textContent)
    } catch (e) {
      console.error("error parsing form-errors JSON", e)
    }

    if (errors && Object.keys(errors).length) {
      form.errors = errors
    }
  }
}

function attachNext(form: DjangoForm) {
  const nextEl = document.getElementById("next-json")
  if (nextEl && nextEl.textContent.startsWith('"')) {
    let next = null
    try {
      next = JSON.parse(nextEl.textContent)
    } catch (e) {
      console.error("error parsing next-json", e)
    }
    if (next) {
      form.next = next
    }
  }
}

export const useDjangoForm = () => {
  // if an element with id=form-errors exists, parse it as JSON
  const form: DjangoForm = {}

  attachErrors(form)
  attachNext(form)

  return form
}
