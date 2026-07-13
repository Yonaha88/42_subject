/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_put.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/03 11:45:56 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/08 16:34:28 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

int	ft_putchar(char c, int len)
{
	if (write(1, &c, 1) == -1)
		return (-1);
	return (len + 1);
}

int	ft_putstr(const char *str, int len)
{
	int	idx;
	int	written;

	idx = 0;
	if (str == NULL)
	{
		written = write(1, "(null)", 6);
		return (len + written);
	}
	while (str[idx])
		idx++;
	written = write(1, str, idx);
	if (written == -1)
		return (written);
	return (len + written);
}

int	ft_puthex(unsigned long long n, int len, const char *hex_base)
{
	if (n == 0)
		return (ft_putchar('0', len));
	if (n >= 16)
	{
		len = ft_puthex(n / 16, len, hex_base);
		if (len == -1)
			return (-1);
	}
	return (ft_putchar(hex_base[n % 16], len));
}

int	ft_putnbr(long n, int len)
{
	char	*nbr;

	nbr = ft_itoa(n);
	if (!nbr)
		return (-1);
	len = ft_putstr(nbr, len);
	free(nbr);
	return (len);
}

int	ft_putptr(void *n, int len, const char *hex_base)
{
	if (n == NULL)
	{
		len = ft_putstr("(nil)", len);
		return (len);
	}
	len = ft_putstr("0x", len);
	len = ft_puthex((unsigned long long)n, len, hex_base);
	return (len);
}
