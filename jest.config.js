module.exports = {
    roots: ['<rootDir>'],
    moduleFileExtensions: ['js', 'ts', 'tsx', 'json'],
    moduleNameMapper: {
      '^/static(.*)$': '<rootDir>/cen/static$1',
    },
    collectCoverage: true,
    testEnvironment: 'jsdom',
    coveragePathIgnorePatterns: ['/toolkit.js'],
    transform: {
      '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
    },
    "setupFiles": [
        "./setupJest.js"
  ],
  };