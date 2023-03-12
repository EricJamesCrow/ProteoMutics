import React, { useRef } from 'react'

import {
  useDisclosure
} from '@chakra-ui/react'

// styles
import './DropDownMenu.css'

// components
import About from '../pages/menu/About'
import Settings from '../pages/menu/Settings'
import Help from '../pages/menu/Help'
import ExitModal from '../pages/menu/ExitModal'

export default function DropDownMenu() {
  const { isOpen: isAboutOpen, onOpen: onAboutOpen, onClose: onAboutClose } =
    useDisclosure();
  
    const {
    isOpen: isSettingsOpen,
    onOpen: onSettingsOpen,
    onClose: onSettingsClose,
  } = useDisclosure();
  
  const {
    isOpen: isHelpOpen,
    onOpen: onHelpOpen,
    onClose: onHelpClose,
  } = useDisclosure();
  
  const {
    isOpen: isExitOpen,
    onOpen: onExitOpen,
    onClose: onExitClose,
  } = useDisclosure();
  
  const cancelRef = useRef()

  return (
    <>
    <div className="container-for-drop-down-menu-container">
    <div className="drop-down-menu-container">
        <button onClick={onAboutOpen}>About</button>
        <button onClick={onSettingsOpen}>Settings</button>
        <button onClick={onHelpOpen}>Help</button>
        <button onClick={onExitOpen}>Exit</button>
    </div>
    </div>
    <About isOpen={isAboutOpen} onClose={onAboutClose}/>
    <Settings isOpen={isSettingsOpen} onClose={onSettingsClose}/>
    <Help isOpen={isHelpOpen} onClose={onHelpClose}/>
    <ExitModal isOpen={isExitOpen} onClose={onExitClose} cancelRef={cancelRef}/>
    </>
  )
}
