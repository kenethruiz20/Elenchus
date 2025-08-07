'use client';

import Link from 'next/link';
import { Scale, ArrowLeft } from 'lucide-react';

export default function TermsAndConditions() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link 
                href="/"
                className="flex items-center text-gray-600 hover:text-gray-900 transition-colors mr-6"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back
              </Link>
              <div className="flex items-center">
                <Scale className="h-8 w-8 text-blue-600" />
                <span className="ml-2 text-xl font-semibold text-gray-900">Elenchus AI</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-sm">
          <div className="px-8 py-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Terms & Conditions</h1>
            <p className="text-gray-600 mb-8">Last updated: January 2025</p>

            <div className="prose prose-gray max-w-none">
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Acceptance of Terms</h2>
                <p className="text-gray-700 mb-4">
                  By accessing and using Elenchus AI ("the Service"), you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by the above, please do not use this service.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Description of Service</h2>
                <p className="text-gray-700 mb-4">
                  Elenchus AI provides AI-powered legal research and document analysis services. The Service includes but is not limited to:
                </p>
                <ul className="list-disc pl-6 text-gray-700 mb-4">
                  <li>Document upload and analysis</li>
                  <li>Legal research assistance</li>
                  <li>Case law search and citation</li>
                  <li>Brief and argument generation assistance</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. User Responsibilities</h2>
                <p className="text-gray-700 mb-4">
                  As a user of Elenchus AI, you agree to:
                </p>
                <ul className="list-disc pl-6 text-gray-700 mb-4">
                  <li>Provide accurate and complete information when creating your account</li>
                  <li>Maintain the confidentiality of your login credentials</li>
                  <li>Use the Service in compliance with all applicable laws and regulations</li>
                  <li>Not upload confidential client information without proper authorization</li>
                  <li>Verify all AI-generated content before use in legal proceedings</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Professional Responsibility</h2>
                <p className="text-gray-700 mb-4">
                  Elenchus AI is a tool to assist legal professionals. Users maintain full responsibility for:
                </p>
                <ul className="list-disc pl-6 text-gray-700 mb-4">
                  <li>Verifying the accuracy of all research and citations</li>
                  <li>Ensuring compliance with professional ethics rules</li>
                  <li>Maintaining attorney-client privilege and confidentiality</li>
                  <li>Meeting all professional standards and obligations</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Privacy and Data Security</h2>
                <p className="text-gray-700 mb-4">
                  We take your privacy seriously. Our data handling practices are governed by our Privacy Policy. Key points include:
                </p>
                <ul className="list-disc pl-6 text-gray-700 mb-4">
                  <li>Documents are processed securely and not retained longer than necessary</li>
                  <li>We implement industry-standard security measures</li>
                  <li>User data is never shared with third parties without consent</li>
                  <li>Users can request deletion of their data at any time</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Limitations of Liability</h2>
                <p className="text-gray-700 mb-4">
                  Elenchus AI is provided "as is" without warranties of any kind. We disclaim all liability for:
                </p>
                <ul className="list-disc pl-6 text-gray-700 mb-4">
                  <li>Accuracy or completeness of AI-generated content</li>
                  <li>Professional advice or legal opinions</li>
                  <li>Consequential or incidental damages</li>
                  <li>Service interruptions or technical issues</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Subscription and Payment</h2>
                <p className="text-gray-700 mb-4">
                  Some features of Elenchus AI require a paid subscription. By subscribing, you agree to:
                </p>
                <ul className="list-disc pl-6 text-gray-700 mb-4">
                  <li>Pay all fees as described in your chosen plan</li>
                  <li>Automatic renewal unless cancelled</li>
                  <li>Our refund policy as outlined separately</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Termination</h2>
                <p className="text-gray-700 mb-4">
                  We reserve the right to terminate or suspend access to the Service at any time for violations of these terms or other reasons deemed necessary for the protection of our Service or other users.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Changes to Terms</h2>
                <p className="text-gray-700 mb-4">
                  We reserve the right to modify these terms at any time. Users will be notified of significant changes, and continued use constitutes acceptance of modified terms.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Contact Information</h2>
                <p className="text-gray-700 mb-4">
                  If you have questions about these Terms & Conditions, please contact us at:
                </p>
                <p className="text-gray-700">
                  Email: legal@elenchuai.com<br />
                  Address: [Your Business Address]
                </p>
              </section>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}