import React from 'react'

// styles
import './AnalysisBtn.css'

// chakra ui
import {
    Button,
    ButtonGroup,
    Popover,
    PopoverTrigger,
    PopoverContent,
    PopoverHeader,
    PopoverBody,
    PopoverFooter,
    PopoverArrow,
    PopoverCloseButton,
    useDisclosure
  } from '@chakra-ui/react'


export default function AnalysisBtn( { name } ) {
    const { isOpen, onToggle, onClose } = useDisclosure()

  return (
    <Popover
    returnFocusOnClose={false}
    isOpen={isOpen}
    onClose={onClose}
    placement='right'
    closeOnBlur={false}
  >
    <PopoverTrigger>
        <button className="analysis-btn" onClick={onToggle}>{name}</button>
    </PopoverTrigger>
    <PopoverContent>
      <PopoverArrow />
      <PopoverCloseButton />
      <PopoverBody>
        File needs to be preprocessed before analysis. Do you want to begin now?
      </PopoverBody>
      <PopoverFooter display='flex' justifyContent='flex-end'>
        <ButtonGroup size='sm'>
          <Button variant='outline'>No</Button>
          <Button colorScheme='blue'>Yes</Button>
        </ButtonGroup>
      </PopoverFooter>
    </PopoverContent>
  </Popover>
  )
}
