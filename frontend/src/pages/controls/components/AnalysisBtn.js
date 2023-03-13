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


export default function AnalysisBtn( { name, handleFileSelect, allowedFileTypes, type, showLoading, showPreProcessed } ) {
    const { isOpen, onToggle, onClose } = useDisclosure()

    const handleClick = async () => {
      const response = await myApp.showFileDialog(allowedFileTypes);
      if(!response) return;
      showPreProcessed(false)
      showLoading(true)
      const result = await checkIfPreprocessed(response, type)
      handleFileSelect(response, result)
      showLoading(false)
      if(!result) {
        showPreProcessed(true)
        return onToggle()
      }
      return showPreProcessed(true)
    }

    const checkIfPreprocessed = async (file_path, file_type) => {
      const response = await fetch('http://localhost:8000/api/check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({file_path: file_path, type: file_type})
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
