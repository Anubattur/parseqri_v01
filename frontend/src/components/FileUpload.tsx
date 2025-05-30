import React, { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { RiUploadCloud2Line, RiFileLine, RiCloseLine, RiCheckboxCircleLine } from 'react-icons/ri'

interface FileUploadProps {
  onFileUpload: (file: File) => void;
  isUploading: boolean;
}

const FileUpload = ({ onFileUpload, isUploading }: FileUploadProps) => {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      // Check if file is CSV
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        setSelectedFile(file)
        onFileUpload(file)
        showUploadSuccess()
      } else {
        alert('Please upload a CSV file')
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      // Check if file is CSV
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        setSelectedFile(file)
        onFileUpload(file)
        showUploadSuccess()
      } else {
        alert('Please upload a CSV file')
      }
    }
  }

  const showUploadSuccess = () => {
    // Show success message for 3 seconds after upload completes
    setTimeout(() => {
      if (!isUploading) {
        setUploadSuccess(true)
        setTimeout(() => {
          setUploadSuccess(false)
        }, 3000)
      }
    }, 2000)
  }

  const onButtonClick = () => {
    if (inputRef.current) {
      inputRef.current.click()
    }
  }

  const removeFile = () => {
    setSelectedFile(null)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full bg-white dark:bg-dark-900 rounded-xl shadow-md p-6"
    >
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Upload Data</h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        Upload your CSV file to analyze and query your data
      </p>

      <motion.div 
        whileHover={{ scale: dragActive ? 1 : 1.01 }}
        animate={{ 
          borderColor: dragActive ? 'rgb(59, 130, 246)' : 'rgb(209, 213, 219)',
          backgroundColor: dragActive ? 'rgba(59, 130, 246, 0.05)' : 'transparent'
        }}
        transition={{ 
          duration: 0.2, 
          ease: 'easeInOut'
        }}
        className={`border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center transition-colors duration-300 ${
          dragActive 
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/10' 
            : 'border-gray-300 dark:border-dark-700'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {selectedFile ? (
          <motion.div 
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="flex items-center space-x-4"
          >
            <div className="rounded-full bg-primary-50 dark:bg-primary-900/20 p-2">
              <RiFileLine size={24} className="text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {selectedFile.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {(selectedFile.size / 1024).toFixed(2)} KB
              </p>
            </div>
            <button 
              onClick={removeFile} 
              className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-dark-800 transition-colors"
              disabled={isUploading}
            >
              <RiCloseLine size={20} className="text-gray-500 dark:text-gray-400" />
            </button>
          </motion.div>
        ) : (
          <>
            <motion.div 
              animate={{ 
                y: [0, -5, 0],
              }}
              transition={{ 
                duration: 1.5, 
                repeat: Infinity, 
                ease: "easeInOut" 
              }}
              className="mb-3"
            >
              <RiUploadCloud2Line size={48} className="text-gray-400 dark:text-gray-500" />
            </motion.div>
            <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
              Drag and drop your CSV file here, or 
              <button 
                onClick={onButtonClick} 
                className="text-primary-600 dark:text-primary-400 font-medium ml-1 hover:underline"
                disabled={isUploading}
              >
                browse
              </button>
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Only CSV files are supported
            </p>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={handleFileChange}
          disabled={isUploading}
        />
      </motion.div>
      
      <AnimatePresence>
        {isUploading && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-4 flex items-center justify-center"
          >
            <motion.div 
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              className="h-5 w-5 border-2 border-primary-600 border-t-transparent rounded-full mr-2" 
            />
            <p className="text-sm text-gray-700 dark:text-gray-300">Uploading...</p>
          </motion.div>
        )}

        {uploadSuccess && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-4 flex items-center justify-center text-green-600 dark:text-green-400"
          >
            <RiCheckboxCircleLine className="mr-2" />
            <p className="text-sm">File uploaded successfully!</p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default FileUpload 