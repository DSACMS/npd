import { UsaBanner } from "@cmsgov/design-system"
//import './App.css'

function Header() {
  return (
    <>
      <UsaBanner />
      <header className="ds-base--inverse ds-u-padding-y--3">
        <div className="ds-l-container">
          <span className="ds-text-heading--xl">
            National Provider Directory
          </span>
        </div>
      </header>
    </>
  )
}

export default Header
