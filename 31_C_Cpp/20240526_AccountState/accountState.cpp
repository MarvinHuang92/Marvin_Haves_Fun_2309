#include <iostream>
using namespace std;

class AccountState
{
public:
    virtual void deposit(double amount) = 0;
    virtual void withdraw(double amount) = 0;
    virtual void freeze() = 0;
    virtual void unfreeze() = 0;
};

class Account
{
private:
    AccountState* state;
public:
    Account(): state(NULL) {};

    void setState(AccountState* state)
    {
        this -> state = state;
    }

    AccountState* getState()
    {
        return this -> state;
    }

    void deposit(double amount)
    {
        this -> state -> deposit(amount);
    }

    void withdraw(double amount)
    {
        this -> state -> withdraw(amount);
    }

    void freeze()
    {
        this -> state -> freeze();
    }

    void unfreeze()
    {
        this -> state -> unfreeze();
    }
};

class ActiveState: public AccountState
{
public:
    void deposit(double amount)
    {
        cout << "Depositting amount: " << amount << endl;
    }

    void withdraw(double amount)
    {
        cout << "Withdrawing amount: " << amount << endl;
    }

    void freeze()
    {
        cout << "This account will be frozen." << endl;
    }

    void unfreeze()
    {
        cout << "This account is aleady unfrozen." << endl;
    }
};

class FrozenState: public AccountState
{
public:
    void deposit(double amount)
    {
        cout << "This account is frozen, cannot deposit." << endl;
    }

    void withdraw(double amount)
    {
        cout << "This account is frozen, cannot withdraw." << endl;
    }

    void freeze()
    {
        cout << "This account is already frozen." << endl;
    }

    void unfreeze()
    {
        cout << "This account will be unfrozen." << endl;
    }
};


// test
int main()
{
    Account account;
    
    ActiveState* state_Active;
    // cout << "Active State Address: " << state_Active << endl;

    FrozenState* state_Frozen;
    // cout << "Frozen State Address: " << state_Frozen << endl;
    
    AccountState* current_state;
    account.setState(state_Active);
    current_state = account.getState();
    cout << "Current State Address: " << current_state << endl;

    // account.setState(state_Frozen);
    // current_state = account.getState();
    // cout << "Current State Address: " << current_state << endl;

    account.deposit(100.0);  // 问题：这里调用了父类的virtual方法，而不是子类的方法，没有显示内容
    current_state -> deposit(100.0);   // 同样不显示内容

    account.withdraw(100.0);
    account.freeze();
    account.unfreeze();

    return 0;
}

// 在class中，this 如何指代自身？
// 一定要是指针吗，一般的 . 方法行不行？