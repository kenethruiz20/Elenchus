'use client';

import React from 'react';
import Link from 'next/link';
import { MessageSquare, HelpCircle, Mail, Scale } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-50 dark:bg-gray-900 text-gray-700 dark:text-gray-300 border-t border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo and Description */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center mb-4">
              <Scale className="h-6 w-6 text-blue-500" />
              <span className="ml-2 text-lg font-semibold text-gray-900 dark:text-white">Elenchus AI</span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              AI-powered legal research assistant for modern law practices.
            </p>
          </div>

          {/* Quick Access Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Quick Access</h3>
            <ul className="space-y-2">
              <li>
                <Link 
                  href="/support" 
                  className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition flex items-center"
                >
                  <HelpCircle className="w-4 h-4 mr-2" />
                  Support
                </Link>
              </li>
              <li>
                <Link 
                  href="/feedback" 
                  className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition flex items-center"
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Feedback
                </Link>
              </li>
              <li>
                <Link 
                  href="/contact" 
                  className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition flex items-center"
                >
                  <Mail className="w-4 h-4 mr-2" />
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Legal</h3>
            <ul className="space-y-2">
              <li>
                <Link 
                  href="/privacy" 
                  className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition"
                >
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link 
                  href="/terms" 
                  className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition"
                >
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-800">
          <p className="text-sm text-gray-400 dark:text-gray-400 text-gray-600 text-center">
            © 2024 Elenchus AI. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;