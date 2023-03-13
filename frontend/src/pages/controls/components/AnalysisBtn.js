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
    PopoverBody,
    PopoverFooter,
    PopoverArrow,
    PopoverCloseButton,
    useDisclosure
  } from '@chakra-ui/react'


export default function AnalysisBtn( { name, allowedFileTypes, type } ) {
    const { isOpen, onToggle, onClose } = useDisclosure()

    const handleClick = async () => {
      const response = await myApp.showFileDialog(allowedFileTypes);
      const result = await checkIfPreprocessed(response, type)
      if(!result) {
        return onToggle()
      }
    }

    const checkIfPreprocessed = async (file_path, file_type) => {
      const response = await fetch('http://127.0.0.1:8000/api/check', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({file_path, file_type})
      });
      const data = await response.json();
      return data.is_preprocessed;
    }

  return (
    <Popover
    returnFocusOnClose={false}
    isOpen={isOpen}
    onClose={onClose}
    placement='right'
    closeOnBlur={false}
  >
    <PopoverTrigger>
        <button className="analysis-btn" onClick={handleClick}>{name}</button>
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
