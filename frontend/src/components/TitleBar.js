import React from 'react'

// styles
import './TitleBar.css'

// chakra ui icons
import { HamburgerIcon, MinusIcon, CloseIcon } from '@chakra-ui/icons'

// images
import Maximize from '../images/maximize_icon.svg'
import Restore from '../images/restore_icon.svg'


export default function TitleBar() {
  async function minimize () {
    await myApp.minimizeWindow();
  }
  async function maximize () {
    await myApp.maximizeWindow();
  }
  async function close () {
    await myApp.closeWindow();
  }
  return (
    <div className="title-bar-container drag">
      <div className="hamburger-menu no-drag">
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
  )
}
