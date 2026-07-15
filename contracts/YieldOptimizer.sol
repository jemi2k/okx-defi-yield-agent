// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title YieldOptimizer
 * @notice Core strategy vault for OKX.AI DeFi Yield Optimizer Agent
 * @dev Deployed on X Layer (OKX's Ethereum L2) for low fees
 */
contract YieldOptimizer {
    address public owner;
    
    struct Strategy {
        string name;
        address protocolAddress;
        string protocolName;
        uint256 minDeposit;
        uint256 maxDeposit;
        uint256 currentApy;
        bool active;
        uint256 totalDeposits;
    }
    
    struct UserPosition {
        uint256 strategyId;
        uint256 amount;
        uint256 depositedAt;
        uint256 lastHarvestedAt;
    }
    
    mapping(uint256 => Strategy) public strategies;
    uint256 public strategyCount;
    
    mapping(address => UserPosition[]) public userPositions;
    mapping(address => uint256) public userTotalDeposits;
    
    event StrategyAdded(uint256 indexed strategyId, string name, address protocol);
    event StrategyUpdated(uint256 indexed strategyId, uint256 newApy);
    event Deposit(address indexed user, uint256 indexed strategyId, uint256 amount);
    event Withdrawal(address indexed user, uint256 indexed strategyId, uint256 amount);
    event YieldHarvested(address indexed user, uint256 indexed strategyId, uint256 yieldAmount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    // ========== ADMIN FUNCTIONS ==========
    
    function addStrategy(
        string memory _name,
        address _protocolAddress,
        string memory _protocolName,
        uint256 _minDeposit,
        uint256 _maxDeposit,
        uint256 _initialApy
    ) external onlyOwner {
        strategyCount++;
        strategies[strategyCount] = Strategy({
            name: _name,
            protocolAddress: _protocolAddress,
            protocolName: _protocolName,
            minDeposit: _minDeposit,
            maxDeposit: _maxDeposit,
            currentApy: _initialApy,
            active: true,
            totalDeposits: 0
        });
        emit StrategyAdded(strategyCount, _name, _protocolAddress);
    }

    function updateStrategyApy(uint256 _strategyId, uint256 _newApy) external onlyOwner {
        require(_strategyId <= strategyCount && _strategyId > 0, "Invalid strategy");
        strategies[_strategyId].currentApy = _newApy;
        emit StrategyUpdated(_strategyId, _newApy);
    }

    function toggleStrategy(uint256 _strategyId, bool _active) external onlyOwner {
        require(_strategyId <= strategyCount && _strategyId > 0, "Invalid strategy");
        strategies[_strategyId].active = _active;
    }

    // ========== USER FUNCTIONS ==========
    
    function deposit(uint256 _strategyId) external payable {
        require(_strategyId <= strategyCount && _strategyId > 0, "Invalid strategy");
        Strategy storage strat = strategies[_strategyId];
        require(strat.active, "Strategy not active");
        require(msg.value >= strat.minDeposit, "Below minimum deposit");
        require(strat.totalDeposits + msg.value <= strat.maxDeposit, "Exceeds max deposit");
        
        userPositions[msg.sender].push(UserPosition({
            strategyId: _strategyId,
            amount: msg.value,
            depositedAt: block.timestamp,
            lastHarvestedAt: block.timestamp
        }));
        
        strat.totalDeposits += msg.value;
        userTotalDeposits[msg.sender] += msg.value;
        
        emit Deposit(msg.sender, _strategyId, msg.value);
    }

    function withdraw(uint256 _positionIndex) external {
        require(_positionIndex < userPositions[msg.sender].length, "Invalid position");
        UserPosition storage pos = userPositions[msg.sender][_positionIndex];
        uint256 amount = pos.amount;
        
        // Calculate yield
        uint256 yieldAmount = calculateYield(pos);
        
        // Update strategy
        strategies[pos.strategyId].totalDeposits -= amount;
        userTotalDeposits[msg.sender] -= amount;
        
        // Remove position
        pos.amount = 0;
        
        // Send back principal + yield
        (bool sent, ) = payable(msg.sender).call{value: amount + yieldAmount}("");
        require(sent, "Transfer failed");
        
        emit Withdrawal(msg.sender, pos.strategyId, amount);
        if (yieldAmount > 0) {
            emit YieldHarvested(msg.sender, pos.strategyId, yieldAmount);
        }
    }

    function harvestYield(uint256 _positionIndex) external {
        require(_positionIndex < userPositions[msg.sender].length, "Invalid position");
        UserPosition storage pos = userPositions[msg.sender][_positionIndex];
        require(pos.amount > 0, "Position closed");
        
        uint256 yieldAmount = calculateYield(pos);
        pos.lastHarvestedAt = block.timestamp;
        
        if (yieldAmount > 0) {
            (bool sent, ) = payable(msg.sender).call{value: yieldAmount}("");
            require(sent, "Transfer failed");
            emit YieldHarvested(msg.sender, pos.strategyId, yieldAmount);
        }
    }

    // ========== VIEW FUNCTIONS ==========
    
    function calculateYield(UserPosition memory _pos) public view returns (uint256) {
        Strategy storage strat = strategies[_pos.strategyId];
        uint256 timeElapsed = block.timestamp - _pos.lastHarvestedAt;
        // Simple APY calculation (scaled for demo)
        // yield = amount * apy * time / 365 days / 10000 (apy in basis points)
        return (_pos.amount * strat.currentApy * timeElapsed) / (365 days * 10000);
    }

    function getUserPositions(address _user) external view returns (UserPosition[] memory) {
        return userPositions[_user];
    }

    function getAllStrategies() external view returns (Strategy[] memory) {
        Strategy[] memory allStrats = new Strategy[](strategyCount);
        for (uint256 i = 1; i <= strategyCount; i++) {
            allStrats[i-1] = strategies[i];
        }
        return allStrats;
    }

    function getBestStrategy() external view returns (uint256 bestId, uint256 bestApy) {
        bestApy = 0;
        for (uint256 i = 1; i <= strategyCount; i++) {
            if (strategies[i].active && strategies[i].currentApy > bestApy) {
                bestApy = strategies[i].currentApy;
                bestId = i;
            }
        }
    }
    
    // Allow contract to receive ETH
    receive() external payable {}
}