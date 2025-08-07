'use client';

import { useState } from 'react';
import Link from 'next/link';
import { 
  ArrowRight, 
  FileText, 
  Search, 
  Scale, 
  BookOpen,
  Briefcase,
  Shield,
  CheckCircle,
  Menu,
  X
} from 'lucide-react';

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-gray-50/80 backdrop-blur-md border-b border-gray-100 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Scale className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-semibold text-gray-900">Elenchus AI</span>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-700 hover:text-blue-600 transition">Features</a>
              <a href="#how-it-works" className="text-gray-700 hover:text-blue-600 transition">How it Works</a>
              <a href="#use-cases" className="text-gray-700 hover:text-blue-600 transition">Use Cases</a>
              <Link href="/application" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                Try Elenchus
              </Link>
            </div>

            <button 
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-gray-50 border-b">
            <div className="px-2 pt-2 pb-3 space-y-1">
              <a href="#features" className="block px-3 py-2 text-gray-700 hover:text-blue-600">Features</a>
              <a href="#how-it-works" className="block px-3 py-2 text-gray-700 hover:text-blue-600">How it Works</a>
              <a href="#use-cases" className="block px-3 py-2 text-gray-700 hover:text-blue-600">Use Cases</a>
              <Link href="/application" className="block px-3 py-2 bg-blue-600 text-white rounded-lg">
                Try Elenchus
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 animate-fadeIn">
              Your AI-Powered
              <span className="text-blue-600"> Legal Research</span> Assistant
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto animate-fadeIn animation-delay-200">
              Transform how you analyze case law, statutes, and legal documents. 
              Elenchus AI understands complex legal concepts and helps you build stronger arguments faster.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fadeIn animation-delay-400">
              <Link 
                href="/application" 
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition hover:scale-105 transform"
              >
                Start Research Now
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <button className="inline-flex items-center px-6 py-3 bg-gray-50 text-gray-700 font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition hover:scale-105 transform">
                Watch Demo
              </button>
            </div>
          </div>

          {/* Hero Image Placeholder */}
          <div className="mt-16 relative animate-scaleIn animation-delay-600">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-shadow">
              <div className="bg-gray-50 rounded-lg shadow-lg p-6">
                <div className="flex items-center mb-4">
                  <FileText className="h-6 w-6 text-blue-600 mr-2" />
                  <span className="font-semibold">Legal Document Analysis</span>
                </div>
                <div className="space-y-3">
                  <div className="h-4 bg-gray-200 rounded w-full animate-pulse"></div>
                  <div className="h-4 bg-gray-200 rounded w-5/6 animate-pulse animation-delay-200"></div>
                  <div className="h-4 bg-gray-200 rounded w-4/6 animate-pulse animation-delay-400"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Built for Legal Professionals
            </h2>
            <p className="text-xl text-gray-600">
              Powerful features designed to streamline your legal research workflow
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-gray-50 p-8 rounded-xl shadow-sm hover:shadow-lg transition-all hover:-translate-y-1 transform">
              <Search className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-3">Intelligent Case Search</h3>
              <p className="text-gray-600">
                Find relevant precedents and case law with AI-powered semantic search that understands legal context and terminology.
              </p>
            </div>

            <div className="bg-gray-50 p-8 rounded-xl shadow-sm hover:shadow-lg transition-all hover:-translate-y-1 transform">
              <BookOpen className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-3">Document Analysis</h3>
              <p className="text-gray-600">
                Upload briefs, contracts, and legal documents. Get instant summaries, key points, and relevant citations.
              </p>
            </div>

            <div className="bg-gray-50 p-8 rounded-xl shadow-sm hover:shadow-lg transition-all hover:-translate-y-1 transform">
              <Briefcase className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-3">Brief Generation</h3>
              <p className="text-gray-600">
                Create compelling legal arguments with AI assistance. Generate outlines, arguments, and supporting documentation.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How Elenchus Works
            </h2>
            <p className="text-xl text-gray-600">
              Three simple steps to revolutionize your legal research
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Upload Your Documents</h3>
              <p className="text-gray-600">
                Import case files, briefs, contracts, or any legal documents you need to analyze.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Ask Questions</h3>
              <p className="text-gray-600">
                Query your documents naturally. Ask about precedents, summarize arguments, or explore legal concepts.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Get Insights</h3>
              <p className="text-gray-600">
                Receive comprehensive analysis, relevant citations, and actionable insights to strengthen your case.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section id="use-cases" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Trusted by Legal Professionals
            </h2>
            <p className="text-xl text-gray-600">
              See how Elenchus AI transforms legal research across practice areas
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-gray-50 p-8 rounded-xl shadow-sm">
              <div className="flex items-start mb-4">
                <Shield className="h-8 w-8 text-blue-600 mr-3 flex-shrink-0" />
                <div>
                  <h3 className="text-xl font-semibold mb-2">Litigation Support</h3>
                  <p className="text-gray-600 mb-4">
                    Quickly analyze opposing counsel's briefs, find supporting precedents, and identify weaknesses in arguments.
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center text-sm text-gray-700">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                      Case law research in minutes, not hours
                    </div>
                    <div className="flex items-center text-sm text-gray-700">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                      Automated brief summarization
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 p-8 rounded-xl shadow-sm">
              <div className="flex items-start mb-4">
                <FileText className="h-8 w-8 text-blue-600 mr-3 flex-shrink-0" />
                <div>
                  <h3 className="text-xl font-semibold mb-2">Contract Review</h3>
                  <p className="text-gray-600 mb-4">
                    Analyze contracts for potential issues, compare against standard clauses, and ensure compliance.
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center text-sm text-gray-700">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                      Identify risky clauses instantly
                    </div>
                    <div className="flex items-center text-sm text-gray-700">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                      Compare against industry standards
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Transform Your Legal Research?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of legal professionals using AI to work smarter, not harder.
          </p>
          <Link 
            href="/application" 
            className="inline-flex items-center px-8 py-4 bg-gray-50 text-blue-600 font-semibold rounded-lg hover:bg-gray-100 transition"
          >
            Get Started Free
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <Scale className="h-6 w-6 text-blue-400" />
                <span className="ml-2 text-white font-semibold">Elenchus AI</span>
              </div>
              <p className="text-sm">
                AI-powered legal research for modern law practices.
              </p>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">Features</a></li>
                <li><a href="#" className="hover:text-white transition">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition">Security</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition">Blog</a></li>
                <li><Link href="/faq" className="hover:text-white transition">FAQ</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">Privacy Policy</a></li>
                <li><Link href="/terms" className="hover:text-white transition">Terms of Service</Link></li>
                <li><a href="#" className="hover:text-white transition">Bar Compliance</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm">
            <p>&copy; 2024 Elenchus AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}