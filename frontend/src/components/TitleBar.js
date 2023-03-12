import React, { useState } from 'react';

// styles
import './TitleBar.css'

// chakra ui icons
import { HamburgerIcon, MinusIcon, CloseIcon } from '@chakra-ui/icons'

// images
import Maximize from '../images/maximize_icon.svg'

// components
import DropDownMenu from './DropDownMenu'

export default function TitleBar() {
  const [showMenu, setShowMenu] = useState(false);

  async function minimize () {
    await myApp.minimizeWindow();
  }
  async function maximize () {
    await myApp.maximizeWindow();
  }
  async function close () {
    await myApp.closeWindow();
  }

  const toggleMenu = () => {
    setShowMenu(!showMenu)
  }

  return (
    <>
    <div className="title-bar-container drag">
      <div className="hamburger-menu no-drag" onClick={toggleMenu}>
      <HamburgerIcon w={6} h={6} color='white'/>
      </div>
      <div className="window-controls-container no-drag">
        <div onClick={minimize}>
        <MinusIcon w={3} h={3} color='white'/>
        </div>
        <div onClick={maximize}>
        <Maximize/>
        </div>
        <div onClick={close}>
        <CloseIcon w={3} h={3} color='white'/>
        </div>
      </div>
    </div>
    <div className={`dropdown-menu-container ${showMenu ? 'show' : 'hide'}`} onClick={toggleMenu}>
      <DropDownMenu/>
    </div>
    </>
  )
}
