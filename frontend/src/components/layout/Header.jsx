import { Link, useLocation } from 'react-router-dom';
import orionLogo from '../../assets/orionlogo.png';

const navLinks = [
  { name: 'Dashboard', path: '/' },
  { name: 'Profiles', path: '/profiles' },
  { name: 'Job Analysis', path: '/job-analysis' },
];

const Header = () => {
  const location = useLocation();

  return (
    <header className="w-full bg-white border-b border-gray-200 py-6">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center">
          <img src={orionLogo} alt="Orion Logo" className="h-10 w-auto" />
        </Link>
        {/* Navigation */}
        <nav className="flex-1 flex justify-center">
          <ul className="flex space-x-8">
            {navLinks.map(link => (
              <li key={link.name}>
                <Link
                  to={link.path}
                  className={`text-base font-medium hover:text-blue-600 transition-colors ${
                    location.pathname === link.path ? 'text-blue-700 font-semibold' : 'text-gray-800'
                  }`}
                >
                  {link.name}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        {/* Contact Us Button */}
        <a
          href="https://orionesolutions.com/contact-us/"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center px-6 py-2 bg-blue-600 text-white text-base font-semibold rounded-full hover:bg-blue-700 transition-colors"
        >
          Contact Us
        </a>
      </div>
    </header>
  );
};

export default Header; 