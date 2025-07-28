import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, useAnimation } from 'framer-motion'
import { 
  RiDatabase2Line, 
  RiBarChartBoxLine, 
  RiFileTextLine, 
  RiArrowRightLine, 
  RiSparklingLine, 
  RiCodeSSlashLine, 
  RiRocketLine,
  RiUserSearchLine,
  RiLineChartLine
} from 'react-icons/ri'

const LandingPage = () => {
  const [hovered, setHovered] = useState(false)
  const controls = useAnimation()

  const handleHeroHover = () => {
    setHovered(!hovered)
    controls.start({
      scale: hovered ? 1 : 1.05,
      transition: { duration: 0.5 }
    })
  }

  const buttonVariants = {
    hover: {
      scale: 1.05,
      boxShadow: "0px 8px 15px rgba(0, 0, 0, 0.1)",
      transition: {
        type: "spring",
        stiffness: 400,
        damping: 10
      }
    },
    tap: {
      scale: 0.95
    }
  }

  const iconVariants = {
    hidden: { opacity: 0, pathLength: 0, rotate: -180 },
    visible: { 
      opacity: 1, 
      pathLength: 1, 
      rotate: 0,
      transition: { 
        duration: 2,
        ease: "easeInOut",
        delay: 0.3
      }
    }
  }

  const fadeInUp = {
    hidden: { opacity: 0, y: 20 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: i * 0.1,
        duration: 0.5,
        ease: "easeOut"
      }
    })
  }

  // Combined CTA button variants with fadeIn effect
  const ctaButtonVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: i * 0.1,
        duration: 0.5,
        ease: "easeOut"
      }
    }),
    hover: {
      scale: 1.05,
      boxShadow: "0px 8px 15px rgba(0, 0, 0, 0.1)",
      transition: {
        type: "spring",
        stiffness: 400,
        damping: 10
      }
    },
    tap: {
      scale: 0.95
    }
  }

  return (
    <div className="min-h-screen relative">
      {/* Navy Ship Background - Fixed for entire page */}
      <div 
        className="fixed inset-0 z-0"
        style={{
          backgroundImage: 'url(/navy_ship.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundAttachment: 'fixed',
          opacity: 0.7
        }}
      />
      <nav className="bg-white/95  dark:bg-dark-900/95 backdrop-blur-sm shadow-lg border-b border-gray-200/20 dark:border-gray-700/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-20">
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-3">
                <motion.div 
                  className="flex items-center"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  {/* Indian Navy Logo */}
                  <motion.img 
                    src="/navy_logo.png" 
                    alt="Indian Navy Logo" 
                    className="h-16 w-auto mr-3"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    whileHover={{ scale: 1.05 }}
                  />
                  
                  <div className="flex flex-col">
                    <div className="flex items-center text-2xl font-bold text-primary-600">
                      {/* <motion.div 
                        animate={{ rotate: 360 }}
                        transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
                        className="mr-2"
                      >
                        <RiSparklingLine size={24} />
                      </motion.div> */}
                      ParseQRi
                    </div>
                    <motion.p 
              className="text-m text-primary-600 dark:text-primary-600"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ 
                duration: 0.6,
                delay: 0.4,
                ease: "easeOut"
              }}
            >
              Indian Naval Ship Maintanance Authority
            </motion.p>
                  </div>
                </motion.div>
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <motion.div whileHover="hover" whileTap="tap" variants={buttonVariants}>
                <Link 
                  to="/login" 
                  className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 font-medium px-6 py-2.5 rounded-full hover:bg-gray-100/80 dark:hover:bg-gray-700/50 transition-all duration-200 border border-transparent hover:border-primary-200 dark:hover:border-primary-700"
                >
                  Sign in
                </Link>
              </motion.div>
              <motion.div whileHover="hover" whileTap="tap" variants={buttonVariants}>
                <Link 
                  to="/register" 
                  className="bg-primary-600 hover:bg-primary-700 text-white font-medium px-6 py-2.5 rounded-full transition-all duration-200 shadow-md hover:shadow-lg border border-primary-600 hover:border-primary-700"
                >
                  Sign up
                </Link>
              </motion.div>
              
               {/* C2C Advanced Systems Logo */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="flex items-center"
            >
              <motion.img 
                src="/c2c_logo_light.png" 
                alt="C2C Advanced Systems" 
                className="h-12 w-auto"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              />
            </motion.div>
            </div>
          </div>
        </div>
      </nav>

      <main>
        {/* Hero Section */}
        <div className="relative min-h-screen flex items-center justify-center overflow-hidden z-10">
          {/* Hero Content */}
          <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="text-center">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
              onHoverStart={handleHeroHover}
              onHoverEnd={handleHeroHover}
              className="mb-10"
            >
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="text-6xl tracking-tight font-extrabold text-white dark:text-white sm:text-6xl md:text-7xl relative inline-block"
              >
                Transform Your Data Insights with
                <motion.span 
                  animate={controls}
                  className="text-primary-600 font-extrabold dark:text-primary-400  sm:text-6xl md:text-7xl relative inline-block"
                > ParseQRi
                  <motion.div
                    className="absolute -bottom-2 left-0 w-full h-1 bg-primary-600"
                    initial={{ width: 0 }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 1, delay: 0.5 }}
                  />
                </motion.span>
              </motion.h1>
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.6 }}
                className="mt-6 flex justify-center"
              >
                <motion.div 
                  animate={{ 
                    y: [0, -10, 0],
                  }}
                  transition={{ 
                    repeat: Infinity, 
                    duration: 2,
                    repeatType: "reverse" 
                  }}
                  className="text-primary-600"
                >
                  <RiRocketLine size={50} />
                </motion.div>
              </motion.div>
            </motion.div>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="mt-3 max-w-md mx-auto font-semibold text-base text-white dark:text-black-400 sm:text-lg md:mt-1 md:text-2xl md:max-w-4xl"
            >
              Ask questions in plain language and get instant SQL queries, visualizations, and data insights without writing complex code.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="mt-8 max-w-md mx-auto sm:flex sm:justify-center md:mt-8"
            >
              <motion.div 
                className="rounded-full shadow"
                whileHover="hover"
                whileTap="tap"
                variants={buttonVariants}
              >
                <Link
                  to="/register"
                  className="w-full flex items-center justify-center px-8 py-4 border border-transparent text-base font-medium rounded-full text-white bg-primary-600 hover:bg-primary-700 md:text-lg md:px-10"
                >
                  Get Started for Free
                  <motion.div
                    animate={{ x: [0, 5, 0] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                    className="ml-2"
                  >
                    <RiArrowRightLine size={20} />
                  </motion.div>
                </Link>
              </motion.div>
              <motion.div 
                className="mt-3 rounded-full shadow sm:mt-0 sm:ml-3"
                whileHover="hover"
                whileTap="tap"
                variants={buttonVariants}
              >
                <Link
                  to="/login"
                  className="w-full flex items-center justify-center px-8 py-4 border border-transparent text-base font-medium rounded-full text-primary-600 bg-white hover:bg-gray-50 md:text-lg md:px-10"
                >
                  Sign in to Dashboard
                </Link>
              </motion.div>
            </motion.div>
          </div>
        </div>
        </div>

        {/* Features Section */}
        <div className="py-44 bg-white/20 dark:bg-dark-950/20 backdrop-blur-sm relative z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="lg:text-center">
              <motion.h2 
                custom={1}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeInUp}
                className="text-base text-primary-600 dark:text-primary-400 font-semibold tracking-wide uppercase"
              >
                Key Features
              </motion.h2>
              <motion.p 
                custom={2}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeInUp}
                className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl"
              >
                ParseQri combines natural language processing with powerful data analysis tools to make database interactions intuitive and efficient.
              </motion.p>
            </div>

            <div className="mt-16">
              <div className="space-y-10 md:space-y-0 md:grid md:grid-cols-3 md:gap-x-8 md:gap-y-10">
                <motion.div
                  custom={3}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={fadeInUp}
                  whileHover={{ y: -10 }}
                  className="relative bg-white/20 dark:bg-dark-800/30 backdrop-blur-md p-6 rounded-xl shadow-lg border border-white/30 dark:border-gray-700/30"
                >
                  <div className="absolute flex items-center justify-center h-14 w-14 rounded-full bg-primary-500 text-white left-6 -top-7">
                    <motion.div
                      initial="hidden"
                      animate="visible"
                      variants={iconVariants}
                    >
                      <RiCodeSSlashLine className="h-7 w-7" />
                    </motion.div>
                  </div>
                  <div className="mt-8">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">Natural Language to SQL</h3>
                    <p className="mt-2 text-base text-gray-600 dark:text-gray-300">
                      Ask questions in plain English and get accurate SQL queries instantly. No technical knowledge required.
                    </p>
                  </div>
                </motion.div>

                <motion.div
                  custom={4}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={fadeInUp}
                  whileHover={{ y: -10 }}
                  className="relative bg-white/20 dark:bg-dark-800/30 backdrop-blur-md p-6 rounded-xl shadow-lg border border-white/30 dark:border-gray-700/30"
                >
                  <div className="absolute flex items-center justify-center h-14 w-14 rounded-full bg-primary-500 text-white left-6 -top-7">
                    <motion.div
                      initial="hidden"
                      animate="visible"
                      variants={iconVariants}
                    >
                      <RiLineChartLine className="h-7 w-7" />
                    </motion.div>
                  </div>
                  <div className="mt-8">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">Interactive Visualizations</h3>
                    <p className="mt-2 text-base text-gray-600 dark:text-gray-300">
                      Turn query results into meaningful charts and graphs. Customize and export visuals for presentations.
                    </p>
                  </div>
                </motion.div>

                <motion.div
                  custom={5}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={fadeInUp}
                  whileHover={{ y: -10 }}
                  className="relative bg-white/20 dark:bg-dark-800/30 backdrop-blur-md p-6 rounded-xl shadow-lg border border-white/30 dark:border-gray-700/30"
                >
                  <div className="absolute flex items-center justify-center h-14 w-14 rounded-full bg-primary-500 text-white left-6 -top-7">
                    <motion.div
                      initial="hidden"
                      animate="visible"
                      variants={iconVariants}
                    >
                      <RiFileTextLine className="h-7 w-7" />
                    </motion.div>
                  </div>
                  <div className="mt-8">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">CSV File Support</h3>
                    <p className="mt-2 text-base text-gray-600 dark:text-gray-300">
                      Upload and analyze CSV data directly. Get insights from your spreadsheets without database setup.
                    </p>
                  </div>
                </motion.div>
              </div>
            </div>
          </div>
        </div>

        {/* How It Works Section */}
        <div className="py-44 bg-gray-50/30 dark:bg-dark-900/30 backdrop-blur-sm relative z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.div 
              custom={1}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeInUp}
              className="lg:text-center mb-12"
            >
              <h2 className="text-base text-primary-600 font-semibold tracking-wide uppercase">How It Works</h2>
              <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
                Simple Process, Powerful Results
              </p>
            </motion.div>

            <div className="relative">
              {/* Connection line */}
              
              
              <div className="grid md:grid-cols-3 gap-8">
                <motion.div 
                  custom={2}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={fadeInUp}
                  className="relative bg-white/20 dark:bg-dark-800/30 backdrop-blur-md p-6 rounded-xl shadow-lg border border-white/30 dark:border-gray-700/30 z-10"
                  whileHover={{ scale: 1.03 }}
                >
                  <div className="flex justify-center mb-6">
                    <div className="rounded-full bg-primary-100 dark:bg-primary-900/30 p-3">
                      <motion.div
                        animate={{ rotateY: 360 }}
                        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                      >
                        <RiDatabase2Line size={30} className="text-primary-600 dark:text-primary-400" />
                      </motion.div>
                    </div>
                    <div className="absolute -top-3 -left-3 w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-bold">1</div>
                  </div>
                  <h3 className="text-xl font-semibold text-center text-gray-900 dark:text-white mb-3">Upload Your Data</h3>
                  <p className="text-gray-700 dark:text-gray-200 text-center">
                    Simply upload your CSV file or connect to your database to get started.
                  </p>
                </motion.div>

                <motion.div 
                  custom={3}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={fadeInUp}
                  className="relative bg-white/20 dark:bg-dark-800/30 backdrop-blur-md p-6 rounded-xl shadow-lg border border-white/30 dark:border-gray-700/30 z-10"
                  whileHover={{ scale: 1.03 }}
                >
                  <div className="flex justify-center mb-6">
                    <div className="rounded-full bg-primary-100 dark:bg-primary-900/30 p-3">
                      <motion.div
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                      >
                        <RiUserSearchLine size={30} className="text-primary-600 dark:text-primary-400" />
                      </motion.div>
                    </div>
                    <div className="absolute -top-3 -left-3 w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-bold">2</div>
                  </div>
                  <h3 className="text-xl font-semibold text-center text-gray-900 dark:text-white mb-3">Ask Questions</h3>
                  <p className="text-gray-700 dark:text-gray-200 text-center">
                    Type your questions in plain language – no SQL knowledge needed.
                  </p>
                </motion.div>

                <motion.div 
                  custom={4}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={fadeInUp}
                  className="relative bg-white/20 dark:bg-dark-800/30 backdrop-blur-md p-6 rounded-xl shadow-lg border border-white/30 dark:border-gray-700/30 z-10"
                  whileHover={{ scale: 1.03 }}
                >
                  <div className="flex justify-center mb-6">
                    <div className="rounded-full bg-primary-100 dark:bg-primary-900/30 p-3">
                      <motion.div
                        animate={{ 
                          rotate: [0, 10, 0, -10, 0],
                        }}
                        transition={{ 
                          duration: 2, 
                          repeat: Infinity,
                          repeatType: "mirror" 
                        }}
                      >
                        <RiBarChartBoxLine size={30} className="text-primary-600 dark:text-primary-400" />
                      </motion.div>
                    </div>
                    <div className="absolute -top-3 -left-3 w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-bold">3</div>
                  </div>
                  <h3 className="text-xl font-semibold text-center text-gray-900 dark:text-white mb-3">Get Insights</h3>
                  <p className="text-gray-700 dark:text-gray-200 text-center">
                    View SQL queries, visualizations, and actionable insights instantly.
                  </p>
                </motion.div>
              </div>
            </div>
          </div>
        </div>

        {/* Testimonials Section */}
        <div className="py-44 bg-white/40 dark:bg-dark-950/75 backdrop-blur-sm relative z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.div 
              custom={1}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeInUp}
              className="lg:text-center mb-12"
            >
              <h2 className="text-base text-primary-600 dark:text-primary-400 font-semibold tracking-wide uppercase">Testimonials</h2>
              <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
                Trusted by data professionals (As an example)
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  name: "Sarah Johnson",
                  role: "Data Analyst",
                  company: "TechCorp",
                  quote: "ParseQri has completely transformed how I interact with our data. I can get answers in seconds now!"
                },
                {
                  name: "Michael Chen",
                  role: "Product Manager",
                  company: "InnovateCo",
                  quote: "As a non-technical manager, I can finally get the data insights I need without waiting for our data team."
                },
                {
                  name: "Aisha Patel",
                  role: "Database Administrator",
                  company: "DataFirst",
                  quote: "The SQL queries ParseQri generates are clean, efficient and exactly what I would have written myself."
                }
              ].map((testimonial, index) => (
                <motion.div 
                  key={index}
                  custom={index + 2}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={fadeInUp}
                  whileHover={{ y: -5 }}
                  className="bg-white/20 dark:bg-dark-800/30 backdrop-blur-md p-6 rounded-xl shadow-lg border border-white/30 dark:border-gray-700/30"
                >
                  <div className="flex items-center mb-4">
                    <div className="h-12 w-12 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center text-primary-600 dark:text-primary-400 font-bold text-xl">
                      {testimonial.name.charAt(0)}
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">{testimonial.name}</h3>
                      <p className="text-sm text-gray-700 dark:text-gray-200">{testimonial.role}, {testimonial.company}</p>
                    </div>
                  </div>
                  <p className="text-gray-800 dark:text-gray-100 italic font-medium">"{testimonial.quote}"</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-primary-600/40 dark:bg-primary-900/90 backdrop-blur-sm relative z-10">
          <div className="max-w-7xl mx-auto text-center py-24 px-4 sm:py-28 sm:px-6 lg:px-8">
            <motion.h2 
              custom={1}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeInUp}
              className="text-3xl font-extrabold text-white sm:text-4xl"
            >
              <span className="block">Ready to Unlock Insights from Your Data?</span>
            </motion.h2>
            <motion.p 
              custom={2}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeInUp}
              className="mt-4 text-lg leading-6 text-white"
            >
              Join thousands of data professionals who are transforming how they interact with databases.
            </motion.p>
            <motion.div 
              custom={3}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={ctaButtonVariants}
              whileHover="hover"
              whileTap="tap"
              className="mt-8 inline-block"
            >
              <Link
                to="/register"
                className="w-full flex items-center justify-center px-8 py-4 border border-transparent text-base font-medium rounded-full text-primary-600 bg-white hover:bg-primary-50 sm:w-auto"
              >
                Get Started for Free
                <motion.div
                  animate={{ x: [0, 5, 0] }}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                  className="ml-2"
                >
                  <RiArrowRightLine className="inline" />
                </motion.div>
              </Link>
            </motion.div>
          </div>
        </div>
      </main>

      <footer className="bg-white dark:bg-dark-900/85 backdrop-blur-sm relative z-10">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 md:flex md:items-center md:justify-between lg:px-8">
          <div className="flex justify-center space-x-6 md:order-2">
            <Link to="#" className="text-gray-400 hover:text-gray-500">
              About
            </Link>
            <Link to="#" className="text-gray-400 hover:text-gray-500">
              Privacy
            </Link>
            <Link to="#" className="text-gray-400 hover:text-gray-500">
              Terms
            </Link>
          </div>
          <div className="mt-8 md:mt-0 md:order-1">
            <p className="text-center text-base text-gray-400">
              &copy; {new Date().getFullYear()} ParseQri. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage 