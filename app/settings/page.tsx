'use client';

import { useState } from 'react';
import Link from 'next/link';
import AuthProtection from '@/components/AuthProtection';
import { 
  ArrowLeft, 
  User, 
  CreditCard, 
  Settings as SettingsIcon,
  Mail,
  Calendar,
  Shield,
  Check,
  ExternalLink
} from 'lucide-react';
import { useTheme } from '@/app/context/ThemeContext';

function SettingsPageContent() {
  const { theme } = useTheme();
  const [activeTab, setActiveTab] = useState('account');

  // Mock user data (will be replaced with actual auth provider data later)
  const userData = {
    name: 'John Doe',
    email: 'john.doe@lawfirm.com',
    avatar: 'JD',
    joinDate: 'January 2024',
    plan: 'Professional',
    verified: true
  };

  // Mock billing data
  const billingData = {
    plan: 'Professional Plan',
    price: '$49/month',
    nextBilling: 'August 15, 2024',
    paymentMethod: '**** **** **** 4532',
    cardType: 'Visa'
  };

  const tabs = [
    { id: 'account', label: 'Account', icon: User },
    { id: 'billing', label: 'Billing', icon: CreditCard }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link 
                href="/app" 
                className="p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Back to dashboard"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center space-x-2">
                <SettingsIcon className="w-6 h-6 text-gray-600 dark:text-gray-300" />
                <h1 className="text-xl font-semibold text-gray-900 dark:text-white">Settings</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 text-left rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {activeTab === 'account' && (
              <div className="space-y-6">
                {/* Account Information */}
                <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Account Information</h2>
                  
                  {/* Profile Section */}
                  <div className="flex items-start space-x-4 mb-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold text-lg">{userData.avatar}</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{userData.name}</h3>
                        {userData.verified && (
                          <div className="flex items-center space-x-1 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 px-2 py-1 rounded-full text-xs">
                            <Check className="w-3 h-3" />
                            <span>Verified</span>
                          </div>
                        )}
                      </div>
                      <p className="text-gray-600 dark:text-gray-400 mb-2">{userData.email}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-500">Member since {userData.joinDate}</p>
                    </div>
                  </div>

                  {/* Account Details */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          <Mail className="w-4 h-4 inline mr-2" />
                          Email Address
                        </label>
                        <div className="bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2">
                          <span className="text-gray-900 dark:text-gray-100">{userData.email}</span>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          Managed by your Google account
                        </p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          <Calendar className="w-4 h-4 inline mr-2" />
                          Member Since
                        </label>
                        <div className="bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2">
                          <span className="text-gray-900 dark:text-gray-100">{userData.joinDate}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Security Section */}
                  <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
                      <Shield className="w-5 h-5 mr-2" />
                      Security
                    </h3>
                    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                      <div className="flex items-start space-x-3">
                        <Shield className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                        <div>
                          <h4 className="font-medium text-blue-900 dark:text-blue-200">Google Authentication</h4>
                          <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                            Your account is secured with Google's authentication system. 
                            Sign-in settings are managed through your Google account.
                          </p>
                          <button className="mt-2 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 flex items-center">
                            Manage Google Account
                            <ExternalLink className="w-3 h-3 ml-1" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'billing' && (
              <div className="space-y-6">
                {/* Current Plan */}
                <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Current Plan</h2>
                  
                  <div className="flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg mb-6">
                    <div>
                      <h3 className="text-xl font-semibold text-blue-900 dark:text-blue-200">{billingData.plan}</h3>
                      <p className="text-blue-700 dark:text-blue-300">{billingData.price}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-blue-700 dark:text-blue-300">Next billing</p>
                      <p className="font-medium text-blue-900 dark:text-blue-200">{billingData.nextBilling}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-3">Plan Features</h4>
                      <ul className="space-y-2 text-sm">
                        <li className="flex items-center text-gray-700 dark:text-gray-300">
                          <Check className="w-4 h-4 text-green-500 mr-2" />
                          Unlimited document uploads
                        </li>
                        <li className="flex items-center text-gray-700 dark:text-gray-300">
                          <Check className="w-4 h-4 text-green-500 mr-2" />
                          Advanced AI research tools
                        </li>
                        <li className="flex items-center text-gray-700 dark:text-gray-300">
                          <Check className="w-4 h-4 text-green-500 mr-2" />
                          Priority support
                        </li>
                        <li className="flex items-center text-gray-700 dark:text-gray-300">
                          <Check className="w-4 h-4 text-green-500 mr-2" />
                          Team collaboration
                        </li>
                      </ul>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-3">Usage This Month</h4>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-600 dark:text-gray-400">Documents Analyzed</span>
                            <span className="text-gray-900 dark:text-white">47 / Unlimited</span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div className="bg-blue-600 h-2 rounded-full" style={{width: '15%'}}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-600 dark:text-gray-400">AI Queries</span>
                            <span className="text-gray-900 dark:text-white">234 / Unlimited</span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div className="bg-blue-600 h-2 rounded-full" style={{width: '23%'}}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex space-x-3 mt-6">
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      Upgrade Plan
                    </button>
                    <button className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                      View All Plans
                    </button>
                  </div>
                </div>

                {/* Payment Method */}
                <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Payment Method</h2>
                  
                  <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-600 rounded-lg mb-4">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded flex items-center justify-center">
                        <CreditCard className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{billingData.cardType} {billingData.paymentMethod}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Expires 12/27</p>
                      </div>
                    </div>
                    <button className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 text-sm font-medium">
                      Edit
                    </button>
                  </div>

                  <button className="w-full p-3 border-2 border-dashed border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 rounded-lg hover:border-gray-400 dark:hover:border-gray-500 transition-colors">
                    + Add Payment Method
                  </button>
                </div>

                {/* Billing History */}
                <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Billing History</h2>
                  
                  <div className="space-y-3">
                    {[
                      { date: 'July 15, 2024', amount: '$49.00', status: 'Paid', invoice: 'INV-001' },
                      { date: 'June 15, 2024', amount: '$49.00', status: 'Paid', invoice: 'INV-002' },
                      { date: 'May 15, 2024', amount: '$49.00', status: 'Paid', invoice: 'INV-003' },
                    ].map((bill, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
                        <div className="flex items-center space-x-4">
                          <div>
                            <p className="font-medium text-gray-900 dark:text-white">{bill.date}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Professional Plan</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <span className="font-medium text-gray-900 dark:text-white">{bill.amount}</span>
                          <span className="px-2 py-1 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 text-xs rounded-full">
                            {bill.status}
                          </span>
                          <button className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 text-sm">
                            Download
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <AuthProtection>
      <SettingsPageContent />
    </AuthProtection>
  );
}