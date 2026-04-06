'use client'

import { useState } from 'react'
import { Dialog, DialogPanel } from '@headlessui/react'
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline'
import { useNavigate } from 'react-router-dom'
import About from './About'
import BackgroundPolygons from './BackgroundPolygons' // Import the new component
import Navbar from './Navbar'; // Import the Navbar component

const navigation = [
  { name: 'About', href: '/' },
  { name: 'Start Practice', href: '/get-started' },
]

const AboutPage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const navigate = useNavigate()

  return (
    <div className="bg-gradient-to-t from-black via-purple-900 to-gray-900 min-h-screen text-white overflow-hidden">
      {/* Integrate Navbar */}
      <Navbar />

      <div className="relative isolate px-6 pt-16 lg:px-8"> {/* Adjusted pt for fixed navbar */}
        <BackgroundPolygons /> {/* Use the new component */}

        <div className="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56">
          <div className="text-center">
            <h1 className="text-6xl font-bold tracking-tight text-white sm:text-7xl">
              AI Interview Helper
            </h1>
            <p className="mt-6 text-2xl leading-8 text-gray-300">
            Master every interview, one question at a time!
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <button
                onClick={() => navigate('/get-started')}
                className="rounded-md bg-gradient-to-r from-indigo-700 via-indigo-800 to-indigo-900 px-8 py-4 text-3xl font-semibold text-white shadow-lg hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition"
              >
                Get Started
              </button>
             
            </div>
          </div>
        </div>
        {/* Additional Decorative Elements and About Section */}
        <About />
      </div>
    </div>
  )
}

export default AboutPage