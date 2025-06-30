import orionLogo2 from '../../assets/orionlogo2.png';

const Footer = () => (
  <footer className="w-full bg-gray-50 border-t border-gray-200 py-6 mt-12">
    <div className="max-w-7xl mx-auto px-4 flex flex-col items-center justify-center">
      <div className="flex items-center justify-center mt-1">
        <img
          src={orionLogo2}
          alt="Orion Logo 2"
          className="h-8 w-auto mr-2"
          style={{ maxHeight: '32px' }}
        />
        <p className="text-xs text-gray-700">Powered by Orion eSolutions</p>
      </div>
    </div>
  </footer>
);

export default Footer; 