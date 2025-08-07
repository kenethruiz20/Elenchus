'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Scale, ArrowLeft, Search, ChevronDown, ChevronUp } from 'lucide-react';

interface FAQItem {
  id: string;
  question: string;
  answer: string;
}

const faqData: FAQItem[] = [
  {
    id: '1',
    question: 'Is there a free trial available?',
    answer: 'Yes, you can try us for free for 30 days. If you want, we\'ll provide you with a free, personalized 30-minute onboarding call to get you up and running as soon as possible.'
  },
  {
    id: '2',
    question: 'Can I change my plan later?',
    answer: 'Of course! You can upgrade or downgrade your plan at any time from your account settings. Changes will be reflected in your next billing cycle.'
  },
  {
    id: '3',
    question: 'What is your cancellation policy?',
    answer: 'You can cancel your subscription at any time. Your access will continue until the end of your current billing period, and you won\'t be charged again.'
  },
  {
    id: '4',
    question: 'Can other info be added to an invoice?',
    answer: 'Yes, you can add custom information to your invoices such as purchase order numbers, tax IDs, or billing addresses through your account settings.'
  },
  {
    id: '5',
    question: 'How does billing work?',
    answer: 'We bill monthly or annually depending on your chosen plan. All payments are processed securely through Stripe, and you\'ll receive an invoice via email for each payment.'
  },
  {
    id: '6',
    question: 'How do I change my account email?',
    answer: 'You can change your account email in the Account Settings section. You\'ll need to verify the new email address before the change takes effect.'
  },
  {
    id: '7',
    question: 'What file formats are supported?',
    answer: 'Elenchus AI supports PDF, DOC, DOCX, and TXT file formats. We\'re continuously adding support for more formats based on user feedback.'
  },
  {
    id: '8',
    question: 'Is my data secure and confidential?',
    answer: 'Absolutely. We use bank-level encryption and follow strict security protocols. Your documents are processed securely and are never shared with third parties or used to train our models.'
  },
  {
    id: '9',
    question: 'How accurate are the AI-generated responses?',
    answer: 'Our AI is highly accurate but should always be reviewed by a qualified attorney. We recommend verifying all citations and legal references before using them in official documents.'
  },
  {
    id: '10',
    question: 'Can I collaborate with team members?',
    answer: 'Yes, our Pro and Enterprise plans include team collaboration features, allowing you to share documents and research with colleagues securely.'
  }
];

export default function FAQ() {
  const [searchTerm, setSearchTerm] = useState('');
  const [openItems, setOpenItems] = useState<Set<string>>(new Set(['1']));

  const filteredFAQ = faqData.filter(
    item =>
      item.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.answer.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const toggleItem = (id: string) => {
    const newOpenItems = new Set(openItems);
    if (newOpenItems.has(id)) {
      newOpenItems.delete(id);
    } else {
      newOpenItems.add(id);
    }
    setOpenItems(newOpenItems);
  };

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
        <div className="text-center mb-12">
          <p className="text-sm text-gray-500 mb-2">FAQs</p>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Frequently asked questions</h1>
          <p className="text-xl text-gray-600 mb-8">Have questions? We're here to help.</p>
          
          {/* Search Bar */}
          <div className="max-w-md mx-auto relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* FAQ Items */}
        <div className="space-y-4">
          {filteredFAQ.map((item) => (
            <div key={item.id} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <button
                onClick={() => toggleItem(item.id)}
                className="w-full px-6 py-6 text-left flex items-center justify-between hover:bg-gray-50 transition-colors focus:outline-none focus:bg-gray-50"
              >
                <span className="text-lg font-medium text-gray-900">{item.question}</span>
                <div className="ml-4 flex-shrink-0">
                  {openItems.has(item.id) ? (
                    <ChevronUp className="h-5 w-5 text-gray-500" />
                  ) : (
                    <ChevronDown className="h-5 w-5 text-gray-500" />
                  )}
                </div>
              </button>
              
              {openItems.has(item.id) && (
                <div className="px-6 pb-6">
                  <div className="text-gray-700 leading-relaxed">
                    {item.answer}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {filteredFAQ.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No questions found matching your search.</p>
          </div>
        )}

        {/* Contact Section */}
        <div className="mt-16 text-center">
          <div className="bg-gray-100 rounded-xl p-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Still have questions?</h2>
            <p className="text-gray-600 mb-6">Can't find the answer you're looking for? Please chat to our friendly team.</p>
            <Link
              href="/application"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
            >
              Get in touch
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}