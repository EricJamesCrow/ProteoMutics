import React from 'react'

import {
    Button,
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalFooter,
    ModalBody,
    ModalCloseButton,
  } from '@chakra-ui/react'

export default function About({ isOpen, onClose }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
    <ModalOverlay />
    <ModalContent>
      <ModalHeader>About Nucleomutics</ModalHeader>
      <ModalCloseButton />
      <ModalBody>
      <p>Lorem ipsum dolor sit amet, splendide theophrastus nam in, tantas dissentiet ex est, eos purto primis eu. Soluta facilisis consectetuer pri ut. Est in munere fabellas, an iusto tation per.</p>
      </ModalBody>
      <ModalFooter>
        <Button colorScheme='blue' mr={3} onClick={onClose}>
          Close
        </Button>
      </ModalFooter>
    </ModalContent>
  </Modal>
  )
}
