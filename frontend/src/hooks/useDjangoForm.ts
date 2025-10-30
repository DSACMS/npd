// load form

type DjangoFormErrors = {
  [fieldName: string | "__all__"]: string[]
}

type DjangoForm = {
  errors?: DjangoFormErrors
}

export const useDjangoForm = () => {
  // if an element with id=form-errors exists, parse it as JSON
  const form: DjangoForm = {}
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

  return form
}
