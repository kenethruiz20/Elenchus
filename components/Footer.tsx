'use client';

import React from 'react';
import Link from 'next/link';
import { MessageSquare, HelpCircle, Mail, Scale } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 dark:bg-gray-900 bg-gray-100 text-gray-300 dark:text-gray-300 text-gray-700 border-t border-gray-800 dark:border-gray-800 border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo and Description */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center mb-4">
              <Scale className="h-6 w-6 text-blue-500" />
              <span className="ml-2 text-lg font-semibold text-white dark:text-white text-gray-900">Elenchus AI</span>
            </div>
            <p className="text-sm text-gray-400 dark:text-gray-400 text-gray-600">
              AI-powered legal research assistant for modern law practices.
            </p>
          </div>

          {/* Quick Access Links */}
          <div>
            <h3 className="text-sm font-semibold text-white dark:text-white text-gray-900 mb-3">Quick Access</h3>
            <ul className="space-y-2">
              <li>
                <Link 
                  href="/support" 
                  className="text-sm text-gray-400 dark:text-gray-400 text-gray-600 hover:text-white dark:hover:text-white hover:text-gray-900 transition flex items-center"
                >
                  <HelpCircle className="w-4 h-4 mr-2" />
                  Support
                </Link>
              </li>
              <li>
                <Link 
                  href="/feedback" 
                  className="text-sm text-gray-400 dark:text-gray-400 text-gray-600 hover:text-white dark:hover:text-white hover:text-gray-900 transition flex items-center"
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Feedback
                </Link>
              </li>
              <li>
                <Link 
                  href="/contact" 
                  className="text-sm text-gray-400 dark:text-gray-400 text-gray-600 hover:text-white dark:hover:text-white hover:text-gray-900 transition flex items-center"
                >
                  <Mail className="w-4 h-4 mr-2" />
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-sm font-semibold text-white dark:text-white text-gray-900 mb-3">Legal</h3>
            <ul className="space-y-2">
              <li>
                <Link 
                  href="/privacy" 
                  className="text-sm text-gray-400 dark:text-gray-400 text-gray-600 hover:text-white dark:hover:text-white hover:text-gray-900 transition"
                >
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link 
                  href="/terms" 
                  className="text-sm text-gray-400 dark:text-gray-400 text-gray-600 hover:text-white dark:hover:text-white hover:text-gray-900 transition"
                >
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-8 pt-8 border-t border-gray-800 dark:border-gray-800 border-gray-200">
          <p className="text-sm text-gray-400 dark:text-gray-400 text-gray-600 text-center">
            © 2024 Elenchus AI. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;